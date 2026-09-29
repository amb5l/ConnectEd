from __future__ import annotations

import re

from typing import Self, cast

from antlr4 import ParseTreeVisitor, ParserRuleContext

from .vhdl_parser import vhdl_parser as vhp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .vhdl_model import (
        VhdlArchitecture,
        VhdlComponent,
        VhdlDocument,
        VhdlEntity,
        VhdlGeneric,
        VhdlPackage,
        VhdlPort,
        VhdlPortGroup,
    )


def _textOf(ctx : object) -> str:
    text = getattr(ctx, "text", None)
    if isinstance(text, str):
        return text
    raise AttributeError("text")

class VhdlVisitor(ParseTreeVisitor):
    """Visitor to convert ANTLR4 parse tree to VHDL model objects."""

    _model : VhdlDocument

    def __init__(self : Self):
        super().__init__()
        from .vhdl_model import VhdlDocument
        self._model = VhdlDocument()

    def visit(self : Self, tree : ParserRuleContext) -> object | None:
        """Override to safely visit a tree and catch any errors during visiting."""
        try:
            result : object | None
            if isinstance(tree, vhp.Rule_DesignFileContext):
                result = self.visitDesignFile(tree)
            elif isinstance(tree, vhp.Rule_DesignUnitContext):
                result = self.visitDesignUnit(tree)
            elif isinstance(tree, vhp.Rule_LibraryUnitContext):
                result = self.visitLibraryUnit(tree)
            elif isinstance(tree, vhp.Rule_EntityDeclarationContext):
                result = self.visitEntityDeclaration(tree)
            elif isinstance(tree, vhp.Rule_ArchitectureContext):
                result = self.visitArchitecture(tree)
            elif isinstance(tree, vhp.Rule_PackageDeclarationContext):
                result = self.visitPackageDeclaration(tree)
            elif isinstance(tree, vhp.Rule_PackageDeclarativeItemContext):
                result = self.visitRule_PackageDeclarativeItem(tree)
            elif isinstance(tree, vhp.Rule_BlockDeclarativeItemContext):
                result = self.visitRule_BlockDeclarativeItem(tree)
            elif isinstance(tree, vhp.Rule_ComponentDeclarationContext):
                result = self.visitComponentDeclaration(tree)
            else:
                result = None
            return result
        except Exception as e:
            print(f"Warning: Missing visitor method for {type(tree)}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def visitDesignFile(
        self : Self,
        ctx  : vhp.Rule_DesignFileContext
    ) -> VhdlDocument:
        """Visit design file and populate the HDL model."""
        from .vhdl_model import VhdlEntity, VhdlArchitecture, VhdlPackage

        for design_unit_ctx in ctx.rule_DesignUnit():
            result = self.visit(design_unit_ctx)
            if result:
                if isinstance(result, VhdlEntity):
                    self._model.addEntity(result)
                elif isinstance(result, VhdlArchitecture):
                    self._model.addArchitecture(result)
                elif isinstance(result, VhdlPackage):
                    self._model.addPackage(result)
        return self._model

    def visitDesignUnit(
        self : Self,
        ctx  : vhp.Rule_DesignUnitContext
    ) -> VhdlEntity | VhdlArchitecture | VhdlPackage | None:
        """Visit design unit and extract entity if present."""
        from .vhdl_model import VhdlArchitecture, VhdlEntity, VhdlPackage

        library_unit = ctx.rule_LibraryUnit()
        if library_unit is None:
            return None
        result = self.visit(library_unit)
        if isinstance(result, (VhdlEntity, VhdlArchitecture, VhdlPackage)):
            return result
        return None

    def visitLibraryUnit(
        self : Self,
        ctx  : vhp.Rule_LibraryUnitContext
    ) -> VhdlEntity | VhdlArchitecture | VhdlPackage | None:
        """Visit library unit and extract entity, architecture, or package declaration if present."""
        entity_ctx = ctx.rule_EntityDeclaration()
        if entity_ctx is not None:
            return self.visitEntityDeclaration(entity_ctx)
        architecture_ctx = ctx.rule_Architecture()
        if architecture_ctx is not None:
            return self.visitArchitecture(architecture_ctx)
        package_ctx = ctx.rule_PackageDeclaration()
        if package_ctx is not None:
            return self.visitPackageDeclaration(package_ctx)
        return None

    def visitEntityDeclaration(
        self : Self,
        ctx  : vhp.Rule_EntityDeclarationContext
    ) -> VhdlEntity:
        """Visit entity declaration and extract entity information."""
        from .vhdl_model import VhdlEntity

        name = _textOf(ctx.name)
        generic_ctx = ctx.rule_GenericClause()
        generics = self.visitGenericClause(generic_ctx) if generic_ctx is not None else []
        port_ctx = ctx.rule_PortClause()
        port_groups = self.visitPortClause(port_ctx) if port_ctx is not None else []
        return VhdlEntity(name, generics, port_groups)

    def visitArchitecture(
        self : Self,
        ctx  : vhp.Rule_ArchitectureContext
    ) -> VhdlArchitecture:
        """Visit architecture declaration and extract architecture information."""
        from .vhdl_model import VhdlArchitecture, VhdlComponent

        name = _textOf(ctx.name)
        entity_name = _textOf(ctx.entityName)
        architecture = VhdlArchitecture(name, entity_name)
        for item in ctx.declarativeItems:
            item_node = self.visit(item)
            if isinstance(item_node, VhdlComponent):
                architecture.addComponent(item_node)
        return architecture

    def visitComponentDeclaration(
        self : Self,
        ctx  : vhp.Rule_ComponentDeclarationContext
    ) -> VhdlComponent:
        """Visit component declaration and extract component information."""
        from .vhdl_model import VhdlComponent

        name = _textOf(ctx.name)
        generic_ctx = ctx.rule_GenericClause()
        generics = self.visitGenericClause(generic_ctx) if generic_ctx is not None else []
        port_ctx = ctx.rule_PortClause()
        port_groups = self.visitPortClause(port_ctx) if port_ctx is not None else []
        return VhdlComponent(name, generics, port_groups)

    def visitPackageDeclaration(
        self : Self,
        ctx  : vhp.Rule_PackageDeclarationContext
    ) -> VhdlPackage:
        """Visit a package declaration."""
        from .vhdl_model import VhdlPackage, VhdlComponent

        package_name = _textOf(ctx.name)
        package = VhdlPackage(package_name)
        for item in ctx.declarativeItems:
            item_node = self.visit(item)
            if isinstance(item_node, VhdlComponent):
                package.addComponent(item_node)
        return package

    def visitRule_PackageDeclarativeItem(
        self : Self,
        ctx  : vhp.Rule_PackageDeclarativeItemContext
    ) -> VhdlComponent | None:
        """Visit items declared in a package, including component declarations."""
        if ctx.componentDeclaration:
            return self.visitComponentDeclaration(ctx.componentDeclaration)
        return None

    def visitRule_BlockDeclarativeItem(
        self : Self,
        ctx  : vhp.Rule_BlockDeclarativeItemContext
    ) -> VhdlComponent | None:
        """Visit items declared in an architecture block, including component declarations."""
        if ctx.rule_ComponentDeclaration():
            return self.visitComponentDeclaration(ctx.rule_ComponentDeclaration())
        return None

    def visitGenericClause(
        self : Self,
        ctx  : vhp.Rule_GenericClauseContext
    ) -> list[VhdlGeneric]:
        """Extract generics from generic clause."""
        generics : list[VhdlGeneric] = []
        for element_ctx in ctx.rule_InterfaceElement():
            generic = self.visitInterfaceElement(element_ctx)
            if generic is not None:
                generics.append(generic)
        return generics

    def visitInterfaceElement(
        self : Self,
        ctx  : vhp.Rule_InterfaceElementContext
    ) -> VhdlGeneric | None:
        """Extract generic."""
        from .vhdl_model import VhdlGeneric

        declaration = ctx.rule_InterfaceDeclaration()
        if declaration is None:
            return None
        constant = declaration.rule_InterfaceConstantDeclaration()
        if constant is None:
            return None
        identifiers = self.extractIdentifierList(constant.constantNames)
        type_ = self.extractSubtypeIndication(constant.subtypeIndication)
        default = ""
        if constant.defaultValue:
            default = self.extractExpression(constant.defaultValue)
        return VhdlGeneric(identifiers[0], type_, default)

    def visitPortClause(
        self : Self,
        ctx  : vhp.Rule_PortClauseContext
    ) -> list[VhdlPortGroup]:
        """Extract ports from port clause and organize them into groups."""
        from .vhdl_model import VhdlPortGroup

        port_groups   : list[VhdlPortGroup] = []
        current_group : list[VhdlPort] = []
        port_declarations = ctx.rule_InterfaceSignalDeclaration()
        prev_end_line = None
        for i, port_ctx in enumerate(port_declarations):
            port = self.visitInterfaceSignalDeclaration(port_ctx)
            current_start_line = port_ctx.start.line
            current_end_line = port_ctx.stop.line
            group_boundary = False
            if prev_end_line is not None:
                if current_start_line - prev_end_line > 1:  # One or more blank lines
                    group_boundary = True
            if group_boundary and current_group:
                group_name = f"Group {len(port_groups) + 1}"
                port_groups.append(VhdlPortGroup(group_name, current_group))
                current_group = []
            current_group.append(port)
            prev_end_line = current_end_line
            is_last = (i == len(port_declarations) - 1)
            if is_last and current_group:
                group_name = f"Group {len(port_groups) + 1}"
                port_group = VhdlPortGroup(name=group_name, ports=current_group)
                port_groups.append(port_group)
        if len(port_groups) == 1:
            port_groups[0].name = ""
        return port_groups

    def visitInterfaceSignalDeclaration(
        self : Self,
        ctx  : vhp.Rule_InterfaceSignalDeclarationContext
    ) -> VhdlPort:
        """Extract port from interface signal declaration."""
        from .vhdl_model import VhdlPort

        identifiers = self.extractIdentifierList(ctx.rule_IdentifierList())
        mctx = ctx.getChild(2)  # Based on grammar structure
        simple_mode = mctx.rule_SimpleModeIndication()
        mctx = simple_mode.rule_Mode()
        mode = mctx.name.text.lower()
        type_indication = simple_mode.rule_InterfaceTypeIndication()
        datatype = self.extractSubtypeIndication(type_indication.rule_SubtypeIndication())

        # Extract default value if present
        default = ""
        if simple_mode.defaultValue:
            default = self.extractExpression(simple_mode.defaultValue)

        return VhdlPort(identifiers[0], mode, datatype, default)

    def extractIdentifierList(
        self : Self,
        ctx  : vhp.Rule_IdentifierListContext
    ) -> list[str]:
        """Extract identifier list from context."""
        tokens = ctx.LIT_IDENTIFIER()
        return [token.getText() for token in tokens] if tokens else []

    def extractSubtypeIndication(
        self : Self,
        ctx  : vhp.Rule_SubtypeIndicationContext
    ) -> str:
        """Extract subtype indication string preserving whitespace."""
        # Use the source interval to preserve whitespace
        input_stream = ctx.start.getInputStream()
        start_index = ctx.start.start
        stop_index = ctx.stop.stop
        result = input_stream.getText(start_index, stop_index)
        return cast(str, result)

    def extractExpression(
        self : Self,
        ctx  : vhp.Rule_ExpressionContext
    ) -> str:
        """Extract expression as string."""
        return cast(str, ctx.getText())

    @staticmethod
    def extractConstraint(s : str) -> tuple[str, str, str] | None:
        # Normalize case to lowercase
        s = s.lower()
        # Regex: "downto" or "to"
        # preceded by space, digit, or )
        # followed by space, digit, or (
        pattern = r'(?<=[\s\d\)])(downto|to)(?=[\s\d\(])'
        matches = re.findall(pattern, s)
        if len(matches) != 1:
            return None
        parts = re.split(pattern, s)
        if len(parts) != 3 or not parts[0].strip() or not parts[2].strip():
            return None
        left = parts[0].strip()
        direction = parts[1]
        right = parts[2].strip()
        if left and direction and right:
            print(f"left: {left}, direction: {direction}, right: {right}")
            return left, direction, right
        return None
