from src.checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.checkmate.models.Tool import Tool
from src.checkmate.models.Option import Option


class WALAConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        wala = Tool('WALA')

        """How many times should flows from newInstance() calls to casts be analyzed?"""
        reflection_numFlowToCastIterations = Option('numFlowToCastIterations')
        # TODO: Interface for specifying integers, and specifying partial orders.
        wala.add_option(reflection_numFlowToCastIterations)

        """Should calls to method.invoke() be ignored?"""
        reflection_ignoreMethodInvoke = self.make_binary_option('ignoreMethodInvoke')
        reflection_ignoreMethodInvoke.set_more_sound_than('FALSE', 'TRUE')
        wala.add_option(reflection_ignoreMethodInvoke)

        """Should calls to Class.getMethod be modeled only for application classes?"""
        reflection_applicationClassesOnly = self.make_binary_option('applicationClassesOnly')
        reflection_applicationClassesOnly.set_more_sound_than('FALSE', 'TRUE')
        wala.add_option(reflection_applicationClassesOnly)

        """Should calls to reflective methods with string constant arguments be ignored?"""
        reflection_ignoreStringConstants = self.make_binary_option('ignoreStringConstants')
        reflection_ignoreStringConstants.set_more_sound_than('FALSE', 'TRUE')
        wala.add_option(reflection_ignoreStringConstants)

        """Should call graph construction handle possible invocations of static initializer methods?"""
        handleStaticInit = self.make_binary_option('handleStaticInit')
        handleStaticInit.set_more_sound_than('TRUE', 'FALSE')
        wala.add_option(handleStaticInit)

        """Use distinct instance keys for distinct string constants?"""
        useConstantSpecificKeys = self.make_binary_option('useConstantSpecificKeys')
        useConstantSpecificKeys.set_more_precise_than('TRUE', 'FALSE')
        wala.add_option(useConstantSpecificKeys)

        """Should analysis of lexical scoping consider call stacks?"""
        useStacksForLexcialScoping = self.make_binary_option('useStacksForLexicalScoping')
        # TODO: Partial order?
        wala.add_option(useStacksForLexcialScoping)

        """Should global variables be considered lexically scoped from the root node?"""
        useLexicalScopingForGlobals = self.make_binary_option('useLexicalScopingForGlobals')
        # TODO: Partial order?
        wala.add_option(useLexicalScopingForGlobals)

        """Maximum number of nodes that any CallGraph build is allowed to have. -1 means unlimited."""
        maxNumberofNodes = Option('maxNumberOfNodes')
        # TODO: Handle integer inputs.
        # TODO: Add partial order: i < j means j is more sound unless i == -1
        wala.add_option(maxNumberofNodes)

        """Should call graph construction handle arrays of zero-length differently?"""
        handleZeroLengthArray = Option('handleZeroLengthArray')
        # TODO: Partial order?
        wala.add_option(handleZeroLengthArray)

        return wala