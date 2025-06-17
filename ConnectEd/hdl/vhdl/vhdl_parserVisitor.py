# Generated from vhdl_parser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .vhdl_parser import vhdl_parser
else:
    from vhdl_parser import vhdl_parser

# This class defines a complete generic visitor for a parse tree produced by vhdl_parser.

class vhdl_parserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by vhdl_parser#rule_AbsolutePathname.
    def visitRule_AbsolutePathname(self, ctx:vhdl_parser.Rule_AbsolutePathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AccessIncompleteTypeDefinition.
    def visitRule_AccessIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_AccessIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AccessTypeDefinition.
    def visitRule_AccessTypeDefinition(self, ctx:vhdl_parser.Rule_AccessTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ActualDesignator.
    def visitRule_ActualDesignator(self, ctx:vhdl_parser.Rule_ActualDesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ActualPart.
    def visitRule_ActualPart(self, ctx:vhdl_parser.Rule_ActualPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Aggregate.
    def visitRule_Aggregate(self, ctx:vhdl_parser.Rule_AggregateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AliasDeclaration.
    def visitRule_AliasDeclaration(self, ctx:vhdl_parser.Rule_AliasDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AliasDesignator.
    def visitRule_AliasDesignator(self, ctx:vhdl_parser.Rule_AliasDesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AliasIndication.
    def visitRule_AliasIndication(self, ctx:vhdl_parser.Rule_AliasIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Allocator.
    def visitRule_Allocator(self, ctx:vhdl_parser.Rule_AllocatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Architecture.
    def visitRule_Architecture(self, ctx:vhdl_parser.Rule_ArchitectureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArchitectureStatement.
    def visitRule_ArchitectureStatement(self, ctx:vhdl_parser.Rule_ArchitectureStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArrayConstraint.
    def visitRule_ArrayConstraint(self, ctx:vhdl_parser.Rule_ArrayConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArrayIncompleteTypeDefinition.
    def visitRule_ArrayIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_ArrayIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArrayIndexIncompleteType.
    def visitRule_ArrayIndexIncompleteType(self, ctx:vhdl_parser.Rule_ArrayIndexIncompleteTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArrayIndexIncompleteTypeList.
    def visitRule_ArrayIndexIncompleteTypeList(self, ctx:vhdl_parser.Rule_ArrayIndexIncompleteTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ArrayModeViewIndication.
    def visitRule_ArrayModeViewIndication(self, ctx:vhdl_parser.Rule_ArrayModeViewIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Assertion.
    def visitRule_Assertion(self, ctx:vhdl_parser.Rule_AssertionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AssertionStatement.
    def visitRule_AssertionStatement(self, ctx:vhdl_parser.Rule_AssertionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AssociationElement.
    def visitRule_AssociationElement(self, ctx:vhdl_parser.Rule_AssociationElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AssociationList.
    def visitRule_AssociationList(self, ctx:vhdl_parser.Rule_AssociationListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AttributeDeclaration.
    def visitRule_AttributeDeclaration(self, ctx:vhdl_parser.Rule_AttributeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AttributeDesignator.
    def visitRule_AttributeDesignator(self, ctx:vhdl_parser.Rule_AttributeDesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AttributeSpecification.
    def visitRule_AttributeSpecification(self, ctx:vhdl_parser.Rule_AttributeSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_BindingIndication.
    def visitRule_BindingIndication(self, ctx:vhdl_parser.Rule_BindingIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_BlockConfiguration.
    def visitRule_BlockConfiguration(self, ctx:vhdl_parser.Rule_BlockConfigurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_BlockDeclarativeItem.
    def visitRule_BlockDeclarativeItem(self, ctx:vhdl_parser.Rule_BlockDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_BlockSpecification.
    def visitRule_BlockSpecification(self, ctx:vhdl_parser.Rule_BlockSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_BlockStatement.
    def visitRule_BlockStatement(self, ctx:vhdl_parser.Rule_BlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CaseGenerateAlternative.
    def visitRule_CaseGenerateAlternative(self, ctx:vhdl_parser.Rule_CaseGenerateAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CaseGenerateStatement.
    def visitRule_CaseGenerateStatement(self, ctx:vhdl_parser.Rule_CaseGenerateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CaseStatement.
    def visitRule_CaseStatement(self, ctx:vhdl_parser.Rule_CaseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CaseStatementAlternative.
    def visitRule_CaseStatementAlternative(self, ctx:vhdl_parser.Rule_CaseStatementAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Choice.
    def visitRule_Choice(self, ctx:vhdl_parser.Rule_ChoiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Choices.
    def visitRule_Choices(self, ctx:vhdl_parser.Rule_ChoicesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ComponentConfiguration.
    def visitRule_ComponentConfiguration(self, ctx:vhdl_parser.Rule_ComponentConfigurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ComponentDeclaration.
    def visitRule_ComponentDeclaration(self, ctx:vhdl_parser.Rule_ComponentDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ComponentInstantiationStatement.
    def visitRule_ComponentInstantiationStatement(self, ctx:vhdl_parser.Rule_ComponentInstantiationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ComponentSpecification.
    def visitRule_ComponentSpecification(self, ctx:vhdl_parser.Rule_ComponentSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CompositeTypeDefinition.
    def visitRule_CompositeTypeDefinition(self, ctx:vhdl_parser.Rule_CompositeTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_CompoundConfigurationSpecification.
    def visitRule_CompoundConfigurationSpecification(self, ctx:vhdl_parser.Rule_CompoundConfigurationSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentAssertionStatement.
    def visitRule_ConcurrentAssertionStatement(self, ctx:vhdl_parser.Rule_ConcurrentAssertionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentConditionalSignalAssignment.
    def visitRule_ConcurrentConditionalSignalAssignment(self, ctx:vhdl_parser.Rule_ConcurrentConditionalSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentProcedureCallStatement.
    def visitRule_ConcurrentProcedureCallStatement(self, ctx:vhdl_parser.Rule_ConcurrentProcedureCallStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentSelectedSignalAssignment.
    def visitRule_ConcurrentSelectedSignalAssignment(self, ctx:vhdl_parser.Rule_ConcurrentSelectedSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentSignalAssignmentStatement.
    def visitRule_ConcurrentSignalAssignmentStatement(self, ctx:vhdl_parser.Rule_ConcurrentSignalAssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentSimpleSignalAssignment.
    def visitRule_ConcurrentSimpleSignalAssignment(self, ctx:vhdl_parser.Rule_ConcurrentSimpleSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConcurrentStatement.
    def visitRule_ConcurrentStatement(self, ctx:vhdl_parser.Rule_ConcurrentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConditionClause.
    def visitRule_ConditionClause(self, ctx:vhdl_parser.Rule_ConditionClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConditionalExpression.
    def visitRule_ConditionalExpression(self, ctx:vhdl_parser.Rule_ConditionalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConditionalOrUnaffectedExpression.
    def visitRule_ConditionalOrUnaffectedExpression(self, ctx:vhdl_parser.Rule_ConditionalOrUnaffectedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConditionalSignalAssignment.
    def visitRule_ConditionalSignalAssignment(self, ctx:vhdl_parser.Rule_ConditionalSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConditionalWaveforms.
    def visitRule_ConditionalWaveforms(self, ctx:vhdl_parser.Rule_ConditionalWaveformsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConfigurationDeclaration.
    def visitRule_ConfigurationDeclaration(self, ctx:vhdl_parser.Rule_ConfigurationDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConfigurationDeclarativeItem.
    def visitRule_ConfigurationDeclarativeItem(self, ctx:vhdl_parser.Rule_ConfigurationDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConfigurationItem.
    def visitRule_ConfigurationItem(self, ctx:vhdl_parser.Rule_ConfigurationItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConfigurationSpecification.
    def visitRule_ConfigurationSpecification(self, ctx:vhdl_parser.Rule_ConfigurationSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConstantDeclaration.
    def visitRule_ConstantDeclaration(self, ctx:vhdl_parser.Rule_ConstantDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ConstrainedArrayDefinition.
    def visitRule_ConstrainedArrayDefinition(self, ctx:vhdl_parser.Rule_ConstrainedArrayDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Constraint.
    def visitRule_Constraint(self, ctx:vhdl_parser.Rule_ConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ContextDeclaration.
    def visitRule_ContextDeclaration(self, ctx:vhdl_parser.Rule_ContextDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ContextItem.
    def visitRule_ContextItem(self, ctx:vhdl_parser.Rule_ContextItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ContextReference.
    def visitRule_ContextReference(self, ctx:vhdl_parser.Rule_ContextReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DelayMechanism.
    def visitRule_DelayMechanism(self, ctx:vhdl_parser.Rule_DelayMechanismContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DesignFile.
    def visitRule_DesignFile(self, ctx:vhdl_parser.Rule_DesignFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DesignUnit.
    def visitRule_DesignUnit(self, ctx:vhdl_parser.Rule_DesignUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Designator.
    def visitRule_Designator(self, ctx:vhdl_parser.Rule_DesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Direction.
    def visitRule_Direction(self, ctx:vhdl_parser.Rule_DirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DisconnectionSpecification.
    def visitRule_DisconnectionSpecification(self, ctx:vhdl_parser.Rule_DisconnectionSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DiscreteRange.
    def visitRule_DiscreteRange(self, ctx:vhdl_parser.Rule_DiscreteRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_DiscreteIncompleteTypeDefinition.
    def visitRule_DiscreteIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_DiscreteIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementArrayModeViewIndication.
    def visitRule_ElementArrayModeViewIndication(self, ctx:vhdl_parser.Rule_ElementArrayModeViewIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementAssociation.
    def visitRule_ElementAssociation(self, ctx:vhdl_parser.Rule_ElementAssociationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementConstraint.
    def visitRule_ElementConstraint(self, ctx:vhdl_parser.Rule_ElementConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementDeclaration.
    def visitRule_ElementDeclaration(self, ctx:vhdl_parser.Rule_ElementDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementModeIndication.
    def visitRule_ElementModeIndication(self, ctx:vhdl_parser.Rule_ElementModeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementModeViewIndication.
    def visitRule_ElementModeViewIndication(self, ctx:vhdl_parser.Rule_ElementModeViewIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementRecordModeViewIndication.
    def visitRule_ElementRecordModeViewIndication(self, ctx:vhdl_parser.Rule_ElementRecordModeViewIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ElementResolution.
    def visitRule_ElementResolution(self, ctx:vhdl_parser.Rule_ElementResolutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityAspect.
    def visitRule_EntityAspect(self, ctx:vhdl_parser.Rule_EntityAspectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityClass.
    def visitRule_EntityClass(self, ctx:vhdl_parser.Rule_EntityClassContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityClassEntry.
    def visitRule_EntityClassEntry(self, ctx:vhdl_parser.Rule_EntityClassEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityDeclaration.
    def visitRule_EntityDeclaration(self, ctx:vhdl_parser.Rule_EntityDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityDeclarativeItem.
    def visitRule_EntityDeclarativeItem(self, ctx:vhdl_parser.Rule_EntityDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityDesignator.
    def visitRule_EntityDesignator(self, ctx:vhdl_parser.Rule_EntityDesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityNameList.
    def visitRule_EntityNameList(self, ctx:vhdl_parser.Rule_EntityNameListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntitySpecification.
    def visitRule_EntitySpecification(self, ctx:vhdl_parser.Rule_EntitySpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityStatement.
    def visitRule_EntityStatement(self, ctx:vhdl_parser.Rule_EntityStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EntityTag.
    def visitRule_EntityTag(self, ctx:vhdl_parser.Rule_EntityTagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EnumerationLiteral.
    def visitRule_EnumerationLiteral(self, ctx:vhdl_parser.Rule_EnumerationLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_EnumerationTypeDefinition.
    def visitRule_EnumerationTypeDefinition(self, ctx:vhdl_parser.Rule_EnumerationTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExitStatement.
    def visitRule_ExitStatement(self, ctx:vhdl_parser.Rule_ExitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#binaryOp.
    def visitBinaryOp(self, ctx:vhdl_parser.BinaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#primaryOp.
    def visitPrimaryOp(self, ctx:vhdl_parser.PrimaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#unaryOp.
    def visitUnaryOp(self, ctx:vhdl_parser.UnaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExpressionOrUnaffected.
    def visitRule_ExpressionOrUnaffected(self, ctx:vhdl_parser.Rule_ExpressionOrUnaffectedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExternalName.
    def visitRule_ExternalName(self, ctx:vhdl_parser.Rule_ExternalNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExternalConstantName.
    def visitRule_ExternalConstantName(self, ctx:vhdl_parser.Rule_ExternalConstantNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExternalSignalName.
    def visitRule_ExternalSignalName(self, ctx:vhdl_parser.Rule_ExternalSignalNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExternalVariableName.
    def visitRule_ExternalVariableName(self, ctx:vhdl_parser.Rule_ExternalVariableNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ExternalPathname.
    def visitRule_ExternalPathname(self, ctx:vhdl_parser.Rule_ExternalPathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FileDeclaration.
    def visitRule_FileDeclaration(self, ctx:vhdl_parser.Rule_FileDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FileIncompleteTypeDefinition.
    def visitRule_FileIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_FileIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FileOpenInformation.
    def visitRule_FileOpenInformation(self, ctx:vhdl_parser.Rule_FileOpenInformationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FileTypeDefinition.
    def visitRule_FileTypeDefinition(self, ctx:vhdl_parser.Rule_FileTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FloatingIncompleteTypeDefinition.
    def visitRule_FloatingIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_FloatingIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FloatingTypeDefinition.
    def visitRule_FloatingTypeDefinition(self, ctx:vhdl_parser.Rule_FloatingTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ForGenerateStatement.
    def visitRule_ForGenerateStatement(self, ctx:vhdl_parser.Rule_ForGenerateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FormalDesignator.
    def visitRule_FormalDesignator(self, ctx:vhdl_parser.Rule_FormalDesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FormalParameterList.
    def visitRule_FormalParameterList(self, ctx:vhdl_parser.Rule_FormalParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FormalPart.
    def visitRule_FormalPart(self, ctx:vhdl_parser.Rule_FormalPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FullTypeDeclaration.
    def visitRule_FullTypeDeclaration(self, ctx:vhdl_parser.Rule_FullTypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FunctionCall.
    def visitRule_FunctionCall(self, ctx:vhdl_parser.Rule_FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_FunctionSpecification.
    def visitRule_FunctionSpecification(self, ctx:vhdl_parser.Rule_FunctionSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GenerateSpecification.
    def visitRule_GenerateSpecification(self, ctx:vhdl_parser.Rule_GenerateSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GenerateStatement.
    def visitRule_GenerateStatement(self, ctx:vhdl_parser.Rule_GenerateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GenerateStatementBody.
    def visitRule_GenerateStatementBody(self, ctx:vhdl_parser.Rule_GenerateStatementBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GenericClause.
    def visitRule_GenericClause(self, ctx:vhdl_parser.Rule_GenericClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GenericMapAspect.
    def visitRule_GenericMapAspect(self, ctx:vhdl_parser.Rule_GenericMapAspectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GroupConstituent.
    def visitRule_GroupConstituent(self, ctx:vhdl_parser.Rule_GroupConstituentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GroupDeclaration.
    def visitRule_GroupDeclaration(self, ctx:vhdl_parser.Rule_GroupDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GroupTemplateDeclaration.
    def visitRule_GroupTemplateDeclaration(self, ctx:vhdl_parser.Rule_GroupTemplateDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_GuardedSignalSpecification.
    def visitRule_GuardedSignalSpecification(self, ctx:vhdl_parser.Rule_GuardedSignalSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IdentifierList.
    def visitRule_IdentifierList(self, ctx:vhdl_parser.Rule_IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IfGenerateStatement.
    def visitRule_IfGenerateStatement(self, ctx:vhdl_parser.Rule_IfGenerateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IfStatement.
    def visitRule_IfStatement(self, ctx:vhdl_parser.Rule_IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IncompleteSubtypeIndication.
    def visitRule_IncompleteSubtypeIndication(self, ctx:vhdl_parser.Rule_IncompleteSubtypeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IncompleteTypeDeclaration.
    def visitRule_IncompleteTypeDeclaration(self, ctx:vhdl_parser.Rule_IncompleteTypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IncompleteTypeDefinition.
    def visitRule_IncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_IncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IncompleteTypeMark.
    def visitRule_IncompleteTypeMark(self, ctx:vhdl_parser.Rule_IncompleteTypeMarkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IndexConstraint.
    def visitRule_IndexConstraint(self, ctx:vhdl_parser.Rule_IndexConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IndexSubtypeDefinition.
    def visitRule_IndexSubtypeDefinition(self, ctx:vhdl_parser.Rule_IndexSubtypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InstantiatedUnit.
    def visitRule_InstantiatedUnit(self, ctx:vhdl_parser.Rule_InstantiatedUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InstantiationList.
    def visitRule_InstantiationList(self, ctx:vhdl_parser.Rule_InstantiationListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IntegerIncompleteTypeDefinition.
    def visitRule_IntegerIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_IntegerIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IntegerTypeDefinition.
    def visitRule_IntegerTypeDefinition(self, ctx:vhdl_parser.Rule_IntegerTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceConstantDeclaration.
    def visitRule_InterfaceConstantDeclaration(self, ctx:vhdl_parser.Rule_InterfaceConstantDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceDeclaration.
    def visitRule_InterfaceDeclaration(self, ctx:vhdl_parser.Rule_InterfaceDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceElement.
    def visitRule_InterfaceElement(self, ctx:vhdl_parser.Rule_InterfaceElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceFileDeclaration.
    def visitRule_InterfaceFileDeclaration(self, ctx:vhdl_parser.Rule_InterfaceFileDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceFunctionSpecification.
    def visitRule_InterfaceFunctionSpecification(self, ctx:vhdl_parser.Rule_InterfaceFunctionSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceList.
    def visitRule_InterfaceList(self, ctx:vhdl_parser.Rule_InterfaceListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfacePackageDeclaration.
    def visitRule_InterfacePackageDeclaration(self, ctx:vhdl_parser.Rule_InterfacePackageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfacePackageGenericMapAspect.
    def visitRule_InterfacePackageGenericMapAspect(self, ctx:vhdl_parser.Rule_InterfacePackageGenericMapAspectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceProcedureSpecification.
    def visitRule_InterfaceProcedureSpecification(self, ctx:vhdl_parser.Rule_InterfaceProcedureSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceSignalDeclaration.
    def visitRule_InterfaceSignalDeclaration(self, ctx:vhdl_parser.Rule_InterfaceSignalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceSubprogramDeclaration.
    def visitRule_InterfaceSubprogramDeclaration(self, ctx:vhdl_parser.Rule_InterfaceSubprogramDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceSubprogramDefault.
    def visitRule_InterfaceSubprogramDefault(self, ctx:vhdl_parser.Rule_InterfaceSubprogramDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceSubprogramSpecification.
    def visitRule_InterfaceSubprogramSpecification(self, ctx:vhdl_parser.Rule_InterfaceSubprogramSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceTypeDeclaration.
    def visitRule_InterfaceTypeDeclaration(self, ctx:vhdl_parser.Rule_InterfaceTypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceTypeIndication.
    def visitRule_InterfaceTypeIndication(self, ctx:vhdl_parser.Rule_InterfaceTypeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_InterfaceVariableDeclaration.
    def visitRule_InterfaceVariableDeclaration(self, ctx:vhdl_parser.Rule_InterfaceVariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IterationScheme.
    def visitRule_IterationScheme(self, ctx:vhdl_parser.Rule_IterationSchemeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_LibraryClause.
    def visitRule_LibraryClause(self, ctx:vhdl_parser.Rule_LibraryClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_LibraryUnit.
    def visitRule_LibraryUnit(self, ctx:vhdl_parser.Rule_LibraryUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Literal.
    def visitRule_Literal(self, ctx:vhdl_parser.Rule_LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_LoopStatement.
    def visitRule_LoopStatement(self, ctx:vhdl_parser.Rule_LoopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Mode.
    def visitRule_Mode(self, ctx:vhdl_parser.Rule_ModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ModeIndication.
    def visitRule_ModeIndication(self, ctx:vhdl_parser.Rule_ModeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ModeViewDeclaration.
    def visitRule_ModeViewDeclaration(self, ctx:vhdl_parser.Rule_ModeViewDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ModeViewElementDefinition.
    def visitRule_ModeViewElementDefinition(self, ctx:vhdl_parser.Rule_ModeViewElementDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Char.
    def visitRule_Char(self, ctx:vhdl_parser.Rule_CharContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_IndexedName.
    def visitRule_IndexedName(self, ctx:vhdl_parser.Rule_IndexedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleName.
    def visitRule_SimpleName(self, ctx:vhdl_parser.Rule_SimpleNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_External.
    def visitRule_External(self, ctx:vhdl_parser.Rule_ExternalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_AttributeName.
    def visitRule_AttributeName(self, ctx:vhdl_parser.Rule_AttributeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedName.
    def visitRule_SelectedName(self, ctx:vhdl_parser.Rule_SelectedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SliceName.
    def visitRule_SliceName(self, ctx:vhdl_parser.Rule_SliceNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Operator.
    def visitRule_Operator(self, ctx:vhdl_parser.Rule_OperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_NextStatement.
    def visitRule_NextStatement(self, ctx:vhdl_parser.Rule_NextStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_NullStatement.
    def visitRule_NullStatement(self, ctx:vhdl_parser.Rule_NullStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_NumericLiteral.
    def visitRule_NumericLiteral(self, ctx:vhdl_parser.Rule_NumericLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackageBody.
    def visitRule_PackageBody(self, ctx:vhdl_parser.Rule_PackageBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackageBodyDeclarativeItem.
    def visitRule_PackageBodyDeclarativeItem(self, ctx:vhdl_parser.Rule_PackageBodyDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackageDeclaration.
    def visitRule_PackageDeclaration(self, ctx:vhdl_parser.Rule_PackageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackageDeclarativeItem.
    def visitRule_PackageDeclarativeItem(self, ctx:vhdl_parser.Rule_PackageDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackageInstantiationDeclaration.
    def visitRule_PackageInstantiationDeclaration(self, ctx:vhdl_parser.Rule_PackageInstantiationDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PackagePathname.
    def visitRule_PackagePathname(self, ctx:vhdl_parser.Rule_PackagePathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ParameterMapAspect.
    def visitRule_ParameterMapAspect(self, ctx:vhdl_parser.Rule_ParameterMapAspectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ParameterSpecification.
    def visitRule_ParameterSpecification(self, ctx:vhdl_parser.Rule_ParameterSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PartialPathname.
    def visitRule_PartialPathname(self, ctx:vhdl_parser.Rule_PartialPathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PathnameElement.
    def visitRule_PathnameElement(self, ctx:vhdl_parser.Rule_PathnameElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PhysicalIncompleteTypeDefinition.
    def visitRule_PhysicalIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_PhysicalIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PhysicalLiteral.
    def visitRule_PhysicalLiteral(self, ctx:vhdl_parser.Rule_PhysicalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PhysicalTypeDefinition.
    def visitRule_PhysicalTypeDefinition(self, ctx:vhdl_parser.Rule_PhysicalTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PlainReturnStatement.
    def visitRule_PlainReturnStatement(self, ctx:vhdl_parser.Rule_PlainReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PortClause.
    def visitRule_PortClause(self, ctx:vhdl_parser.Rule_PortClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PortMapAspect.
    def visitRule_PortMapAspect(self, ctx:vhdl_parser.Rule_PortMapAspectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Primary.
    def visitRule_Primary(self, ctx:vhdl_parser.Rule_PrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PrivateVariableDeclaration.
    def visitRule_PrivateVariableDeclaration(self, ctx:vhdl_parser.Rule_PrivateVariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PrivateIncompleteTypeDefinition.
    def visitRule_PrivateIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_PrivateIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcedureCall.
    def visitRule_ProcedureCall(self, ctx:vhdl_parser.Rule_ProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcedureCallStatement.
    def visitRule_ProcedureCallStatement(self, ctx:vhdl_parser.Rule_ProcedureCallStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcedureSpecification.
    def visitRule_ProcedureSpecification(self, ctx:vhdl_parser.Rule_ProcedureSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcessDeclarativeItem.
    def visitRule_ProcessDeclarativeItem(self, ctx:vhdl_parser.Rule_ProcessDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcessSensitivityList.
    def visitRule_ProcessSensitivityList(self, ctx:vhdl_parser.Rule_ProcessSensitivityListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProcessStatement.
    def visitRule_ProcessStatement(self, ctx:vhdl_parser.Rule_ProcessStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_PostponedProcessStatement.
    def visitRule_PostponedProcessStatement(self, ctx:vhdl_parser.Rule_PostponedProcessStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeBody.
    def visitRule_ProtectedTypeBody(self, ctx:vhdl_parser.Rule_ProtectedTypeBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeBodyDeclarativeItem.
    def visitRule_ProtectedTypeBodyDeclarativeItem(self, ctx:vhdl_parser.Rule_ProtectedTypeBodyDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeDeclaration.
    def visitRule_ProtectedTypeDeclaration(self, ctx:vhdl_parser.Rule_ProtectedTypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeDeclarativeItem.
    def visitRule_ProtectedTypeDeclarativeItem(self, ctx:vhdl_parser.Rule_ProtectedTypeDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeDefinition.
    def visitRule_ProtectedTypeDefinition(self, ctx:vhdl_parser.Rule_ProtectedTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ProtectedTypeInstantiationDefinition.
    def visitRule_ProtectedTypeInstantiationDefinition(self, ctx:vhdl_parser.Rule_ProtectedTypeInstantiationDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_QualifiedExpression.
    def visitRule_QualifiedExpression(self, ctx:vhdl_parser.Rule_QualifiedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Range.
    def visitRule_Range(self, ctx:vhdl_parser.Rule_RangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RangeConstraint.
    def visitRule_RangeConstraint(self, ctx:vhdl_parser.Rule_RangeConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordConstraint.
    def visitRule_RecordConstraint(self, ctx:vhdl_parser.Rule_RecordConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordElementConstraint.
    def visitRule_RecordElementConstraint(self, ctx:vhdl_parser.Rule_RecordElementConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordElementList.
    def visitRule_RecordElementList(self, ctx:vhdl_parser.Rule_RecordElementListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordElementResolution.
    def visitRule_RecordElementResolution(self, ctx:vhdl_parser.Rule_RecordElementResolutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordResolution.
    def visitRule_RecordResolution(self, ctx:vhdl_parser.Rule_RecordResolutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordTypeDefinition.
    def visitRule_RecordTypeDefinition(self, ctx:vhdl_parser.Rule_RecordTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RecordModeViewIndication.
    def visitRule_RecordModeViewIndication(self, ctx:vhdl_parser.Rule_RecordModeViewIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_RelativePathname.
    def visitRule_RelativePathname(self, ctx:vhdl_parser.Rule_RelativePathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ReportStatement.
    def visitRule_ReportStatement(self, ctx:vhdl_parser.Rule_ReportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ResolutionIndication.
    def visitRule_ResolutionIndication(self, ctx:vhdl_parser.Rule_ResolutionIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ReturnStatement.
    def visitRule_ReturnStatement(self, ctx:vhdl_parser.Rule_ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ScalarIncompleteTypeDefinition.
    def visitRule_ScalarIncompleteTypeDefinition(self, ctx:vhdl_parser.Rule_ScalarIncompleteTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ScalarTypeDefinition.
    def visitRule_ScalarTypeDefinition(self, ctx:vhdl_parser.Rule_ScalarTypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SecondaryUnitDeclaration.
    def visitRule_SecondaryUnitDeclaration(self, ctx:vhdl_parser.Rule_SecondaryUnitDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedExpressions.
    def visitRule_SelectedExpressions(self, ctx:vhdl_parser.Rule_SelectedExpressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedForceAssignment.
    def visitRule_SelectedForceAssignment(self, ctx:vhdl_parser.Rule_SelectedForceAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedName2.
    def visitRule_SelectedName2(self, ctx:vhdl_parser.Rule_SelectedName2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedSignalAssignment.
    def visitRule_SelectedSignalAssignment(self, ctx:vhdl_parser.Rule_SelectedSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedVariableAssignment.
    def visitRule_SelectedVariableAssignment(self, ctx:vhdl_parser.Rule_SelectedVariableAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedWaveformAssignment.
    def visitRule_SelectedWaveformAssignment(self, ctx:vhdl_parser.Rule_SelectedWaveformAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SelectedWaveforms.
    def visitRule_SelectedWaveforms(self, ctx:vhdl_parser.Rule_SelectedWaveformsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SensitivityClause.
    def visitRule_SensitivityClause(self, ctx:vhdl_parser.Rule_SensitivityClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SensitivityList.
    def visitRule_SensitivityList(self, ctx:vhdl_parser.Rule_SensitivityListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SequentialBlockStatement.
    def visitRule_SequentialBlockStatement(self, ctx:vhdl_parser.Rule_SequentialBlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SequentialStatement.
    def visitRule_SequentialStatement(self, ctx:vhdl_parser.Rule_SequentialStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SignalAssignmentStatement.
    def visitRule_SignalAssignmentStatement(self, ctx:vhdl_parser.Rule_SignalAssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SignalDeclaration.
    def visitRule_SignalDeclaration(self, ctx:vhdl_parser.Rule_SignalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SignalList.
    def visitRule_SignalList(self, ctx:vhdl_parser.Rule_SignalListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Signature.
    def visitRule_Signature(self, ctx:vhdl_parser.Rule_SignatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleConfigurationSpecification.
    def visitRule_SimpleConfigurationSpecification(self, ctx:vhdl_parser.Rule_SimpleConfigurationSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleForceAssignment.
    def visitRule_SimpleForceAssignment(self, ctx:vhdl_parser.Rule_SimpleForceAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleModeIndication.
    def visitRule_SimpleModeIndication(self, ctx:vhdl_parser.Rule_SimpleModeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleRange.
    def visitRule_SimpleRange(self, ctx:vhdl_parser.Rule_SimpleRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleReleaseAssignment.
    def visitRule_SimpleReleaseAssignment(self, ctx:vhdl_parser.Rule_SimpleReleaseAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleSignalAssignment.
    def visitRule_SimpleSignalAssignment(self, ctx:vhdl_parser.Rule_SimpleSignalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleWaveformAssignment.
    def visitRule_SimpleWaveformAssignment(self, ctx:vhdl_parser.Rule_SimpleWaveformAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SimpleVariableAssignment.
    def visitRule_SimpleVariableAssignment(self, ctx:vhdl_parser.Rule_SimpleVariableAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramBody.
    def visitRule_SubprogramBody(self, ctx:vhdl_parser.Rule_SubprogramBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramDeclaration.
    def visitRule_SubprogramDeclaration(self, ctx:vhdl_parser.Rule_SubprogramDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramDeclarativeItem.
    def visitRule_SubprogramDeclarativeItem(self, ctx:vhdl_parser.Rule_SubprogramDeclarativeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramInstantiationDeclaration.
    def visitRule_SubprogramInstantiationDeclaration(self, ctx:vhdl_parser.Rule_SubprogramInstantiationDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramKind.
    def visitRule_SubprogramKind(self, ctx:vhdl_parser.Rule_SubprogramKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubprogramSpecification.
    def visitRule_SubprogramSpecification(self, ctx:vhdl_parser.Rule_SubprogramSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubtypeDeclaration.
    def visitRule_SubtypeDeclaration(self, ctx:vhdl_parser.Rule_SubtypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_SubtypeIndication.
    def visitRule_SubtypeIndication(self, ctx:vhdl_parser.Rule_SubtypeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Suffix.
    def visitRule_Suffix(self, ctx:vhdl_parser.Rule_SuffixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Target.
    def visitRule_Target(self, ctx:vhdl_parser.Rule_TargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_TimeoutClause.
    def visitRule_TimeoutClause(self, ctx:vhdl_parser.Rule_TimeoutClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_TypeConversion.
    def visitRule_TypeConversion(self, ctx:vhdl_parser.Rule_TypeConversionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_TypeDeclaration.
    def visitRule_TypeDeclaration(self, ctx:vhdl_parser.Rule_TypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_TypeDefinition.
    def visitRule_TypeDefinition(self, ctx:vhdl_parser.Rule_TypeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_UnboundArrayDefinition.
    def visitRule_UnboundArrayDefinition(self, ctx:vhdl_parser.Rule_UnboundArrayDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_UnspecifiedTypeIndication.
    def visitRule_UnspecifiedTypeIndication(self, ctx:vhdl_parser.Rule_UnspecifiedTypeIndicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_UseClause.
    def visitRule_UseClause(self, ctx:vhdl_parser.Rule_UseClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_ValueReturnStatement.
    def visitRule_ValueReturnStatement(self, ctx:vhdl_parser.Rule_ValueReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_VariableAssignmentStatement.
    def visitRule_VariableAssignmentStatement(self, ctx:vhdl_parser.Rule_VariableAssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_VariableDeclaration.
    def visitRule_VariableDeclaration(self, ctx:vhdl_parser.Rule_VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_WaitStatement.
    def visitRule_WaitStatement(self, ctx:vhdl_parser.Rule_WaitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_Waveform.
    def visitRule_Waveform(self, ctx:vhdl_parser.Rule_WaveformContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by vhdl_parser#rule_WaveformElement.
    def visitRule_WaveformElement(self, ctx:vhdl_parser.Rule_WaveformElementContext):
        return self.visitChildren(ctx)



del vhdl_parser