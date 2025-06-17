from typing import Optional, Self, TYPE_CHECKING

from antlr4 import ParseTreeVisitor, ParserRuleContext

from .vhdl_parser import vhdl_parser as vhp

if TYPE_CHECKING:
    from .vhdl_model import *

class VhdlVisitor(ParseTreeVisitor):
    """Visitor to convert ANTLR4 parse tree to VHDL model objects."""

    _model : 'VhdlDocument'

    def __init__(self : Self):
        super().__init__()
        from .vhdl_model import VhdlDocument
        self._model = VhdlDocument()

    def visit(self : Self, tree : ParserRuleContext):
        """Override visit to handle missing methods gracefully."""
        try:
            if isinstance(tree, vhp.Rule_DesignFileContext):
                result = self.visitDesignFile(tree)
            elif isinstance(tree, vhp.Rule_DesignUnitContext):
                result = self.visitDesignUnit(tree)
            elif isinstance(tree, vhp.Rule_LibraryUnitContext):
                result = self.visitLibraryUnit(tree)
            elif isinstance(tree, vhp.Rule_EntityDeclarationContext):
                result = self.visitEntityDeclaration(tree)
            elif isinstance(tree, vhp.Rule_GenericClauseContext):
                result = self.visitGenericClause(tree)
            elif isinstance(tree, vhp.Rule_PortClauseContext):
                result = self.visitPortClause(tree)
            elif isinstance(tree, vhp.Rule_PackageDeclarationContext):
                result = self.visitPackageDeclaration(tree)
            elif isinstance(tree, vhp.Rule_PackageDeclarativeItemContext):
                result = self.visitRule_PackageDeclarativeItem(tree)
            elif isinstance(tree, vhp.Rule_ComponentDeclarationContext):
                result = self.visitComponentDeclaration(tree)
            else:
                result = None
            return result
        except AttributeError as e:
            print(f"Warning: Missing visitor method for {tree.__class__.__name__}: {e}")
            return None
        except Exception as e:
            print(f"Error visiting {tree.__class__.__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def visitDesignFile(
        self : Self,
        ctx  : vhp.Rule_DesignFileContext
    ) -> 'VhdlDocument':
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
    ) -> Optional['VhdlEntity | VhdlArchitecture | VhdlPackage']:
        """Visit design unit and extract entity if present."""
        if ctx.rule_LibraryUnit():
            return self.visit(ctx.rule_LibraryUnit())
        return None

    def visitLibraryUnit(
        self : Self,
        ctx  : vhp.Rule_LibraryUnitContext
    ) -> Optional['VhdlEntity | VhdlArchitecture | VhdlPackage']:
        """Visit library unit and extract entity or package declaration if present."""
        if ctx.rule_EntityDeclaration():
            return self.visit(ctx.rule_EntityDeclaration())
        elif ctx.rule_PackageDeclaration():
            return self.visitPackageDeclaration(ctx.rule_PackageDeclaration())
        elif ctx.rule_PackageBody():
            return self.visitRule_PackageBody(ctx.rule_PackageBody())
        elif ctx.rule_PackageInstantiationDeclaration():
            return self.visitRule_PackageInstantiationDeclaration(ctx.rule_PackageInstantiationDeclaration())
        return None

    def visitEntityDeclaration(
        self : Self,
        ctx  : vhp.Rule_EntityDeclarationContext
    ) -> 'VhdlEntity':
        """Visit entity declaration and extract entity information."""
        from .vhdl_model import VhdlEntity

        name = ctx.name.text
        generics = self.visitGenericClause(ctx.rule_GenericClause()) \
            if ctx.rule_GenericClause() else []
        port_groups = self.visitPortClause(ctx.rule_PortClause()) \
            if ctx.rule_PortClause() else []
        return VhdlEntity(name, generics, port_groups)

    def visitComponentDeclaration(
        self : Self,
        ctx  : vhp.Rule_ComponentDeclarationContext
    ) -> 'VhdlComponent':
        """Visit component declaration and extract component information."""
        from .vhdl_model import VhdlComponent

        name = ctx.name.text
        generics = self.visitGenericClause(ctx.rule_GenericClause()) \
            if ctx.rule_GenericClause() else []
        port_groups = self.visitPortClause(ctx.rule_PortClause()) \
            if ctx.rule_PortClause() else []
        return VhdlComponent(name, generics, port_groups)

    def visitPackageDeclaration(
        self : Self,
        ctx  : vhp.Rule_PackageDeclarationContext
    ) -> 'VhdlPackage':
        """Visit a package declaration."""
        from .vhdl_model import VhdlPackage, VhdlComponent

        package_name = ctx.name.text
        package = VhdlPackage(package_name)
        for item in ctx.declarativeItems:
            item_node = self.visit(item)
            if isinstance(item_node, VhdlComponent):
                package.components.appendRow(item_node)
        return package

    def visitRule_PackageDeclarativeItem(
        self : Self,
        ctx  : vhp.Rule_PackageDeclarativeItemContext
    ) -> Optional['VhdlComponent']:
        """Visit items declared in a package, including component declarations."""
        if ctx.componentDeclaration:
            return self.visitComponentDeclaration(ctx.componentDeclaration)
        return None

    def visitGenericClause(
        self : Self,
        ctx  : vhp.Rule_GenericClauseContext
    ) -> list['VhdlGeneric']:
        """Extract generics from generic clause."""
        generics = []
        for element_ctx in ctx.rule_InterfaceElement():
            generics.append(self.visitInterfaceElement(element_ctx))
        return generics

    def visitInterfaceElement(
        self : Self,
        ctx  : vhp.Rule_InterfaceElementContext
    ) -> Optional['VhdlGeneric']:
        """Extract generic."""
        from .vhdl_model import VhdlGeneric

        if ctx.rule_InterfaceDeclaration():
            ictx = ctx.rule_InterfaceDeclaration()
            if ictx.rule_InterfaceConstantDeclaration():
                pctx = ictx.rule_InterfaceConstantDeclaration()
                identifiers = self.extractIdentifierList(pctx.constantNames)
                type_ = self.extractSubtypeIndication(pctx.subtypeIndication)
                default = None
                if pctx.defaultValue:
                    default = self.extractExpression(pctx.defaultValue)
                return VhdlGeneric(identifiers[0], type_, default)
        return None

    def visitPortClause(
        self : Self,
        ctx  : vhp.Rule_PortClauseContext
    ) -> list['VhdlPortGroup']:
        """Extract ports from port clause and organize them into groups."""
        from .vhdl_model import VhdlPortGroup

        port_groups = []
        current_group = []
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
                group_name = f"Group{len(port_groups) + 1}"
                port_group = VhdlPortGroup(name=group_name, ports=current_group)
                port_groups.append(port_group)
        return port_groups

    def visitInterfaceSignalDeclaration(
        self : Self,
        ctx  : vhp.Rule_InterfaceSignalDeclarationContext
    ) -> 'VhdlPort':
        """Extract port from interface signal declaration."""
        from .vhdl_model import VhdlPort

        identifiers = self.extractIdentifierList(ctx.rule_IdentifierList())
        mctx = ctx.getChild(2)  # Based on grammar structure
        simple_mode = mctx.rule_SimpleModeIndication()
        mctx = simple_mode.rule_Mode()
        mode = mctx.name.text.lower()
        type_indication = simple_mode.rule_InterfaceTypeIndication()
        datatype = self.extractSubtypeIndication(type_indication.rule_SubtypeIndication())
        return VhdlPort(identifiers[0], mode, datatype)

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
        return result

    def extractExpression(
        self : Self,
        ctx  : vhp.Rule_ExpressionContext
    ) -> str:
        """Extract expression as string."""
        return ctx.getText()