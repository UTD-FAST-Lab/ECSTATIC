from src.checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool


class DOOPConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        doop = Tool("DOOP")

        analysis = Option("analysis")
        analysis_levels = ['1-call-site-sensitive',
                           '1-call-site-sensitive+heap',
                           '1-object-1-type-sensitive+heap',
                           '1-object-sensitive',
                           '1-object-sensitive+heap',
                           '1-type-sensitive',
                           '1-type-sensitive+heap',
                           '2-call-site-sensitive+2-heap',
                           '2-call-site-sensitive+heap',
                           '2-object-sensitive+2-heap',
                           '2-object-sensitive+heap',
                           '2-type-object-sensitive+2-heap',
                           '2-type-object-sensitive+heap',
                           '2-type-sensitive+heap',
                           '3-object-sensitive+3-heap',
                           '3-type-sensitive+2-heap',
                           '3-type-sensitive+3-heap',
                           'adaptive-2-object-sensitive+heap',
                           'basic-only',
                           'context-insensitive',
                           'context-insensitive-plus',
                           'context-insensitive-plusplus',
                           'data-flow',
                           'dependency-analysis',
                           'fully-guided-context-sensitive',
                           'micro',
                           'partitioned-2-object-sensitive+heap',
                           'selective-2-object-sensitive+heap',
                           'sound-may-point-to',
                           'sticky-2-object-sensitive']

        [analysis.add_level(l) for l in analysis_levels]
        analysis.set_more_precise_than('1-call-site-sensitive+heap', '1-call-site-sensitive')
        analysis.set_more_precise_than('1-object-1-type-sensitive+heap', '1-object-sensitive+heap')
        analysis.set_more_precise_than('1-object-1-type-sensitive+heap', '1-type-sensitive+heap')
        analysis.set_more_precise_than('1-object-sensitive+heap', '1-object-sensitive')
        analysis.set_more_precise_than('1-type-sensitive+heap', '1-type-sensitive')
        analysis.set_more_precise_than('1-object-sensitive+heap', '1-type-sensitive+heap')
        analysis.set_more_precise_than('1-object-sensitive', '1-type-sensitive')
        analysis.set_more_precise_than('2-call-site-sensitive+2-heap', '2-call-site-sensitive+heap')
        analysis.set_more_precise_than('2-call-site-sensitive+heap', '1-call-site-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+heap', '1-object-1-type-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+2-heap', '2-object-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+heap', '2-type-sensitive+heap')
        analysis.set_more_precise_than('3-object-sensitive+3-heap', '2-object-sensitive+2-heap')
        analysis.set_more_precise_than('3-object-sensitive+3-heap', '3-type-sensitive+3-heap')
        analysis.set_more_precise_than('1-call-site-sensitive', 'context-insensitive')
        analysis.set_more_precise_than('1-type-sensitive', 'context-insensitive')

        doop.add_option(analysis)

        """Aggressively merge allocation sites for all regular object types, in lib and app alike."""
        cgas = self.make_binary_option('coarse-grained-allocation-sites')
        cgas.set_more_precise_than('FALSE', 'TRUE')
        doop.add_option(cgas)

        """Enable constant folding logic."""
        cf = self.make_binary_option('constant-folding')
        #TODO: What effect does constant folding have?
        doop.add_option(cf)

        """Enable context-sensitive analysis for internal library objects."""
        cs_library = self.make_binary_option('cs-library')
        cs_library.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(cs_library)

        """Do not merge exception objects"""
        disable_merge_exceptions = self.make_binary_option('disable-merge-exceptions')
        disable_merge_exceptions.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(disable_merge_exceptions)

        """Avoids merging string buffer objects (not recommended)."""
        distinguish_buffers = self.make_binary_option('distinguish-all-string-buffers')
        distinguish_buffers.set_more_precise_than('TRUE','FALSE')
        doop.add_option(distinguish_buffers)

        """Treat string constants as regular objects."""
        distinguish_string_consts = self.make_binary_option('distinguish-all-string-constants')
        distinguish_string_consts.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(distinguish_string_consts)

        """Disable the default policy of merging library 
        (non-collection) objects of the same type per-method."""
        no_merge_library = self.make_binary_option('no-merge-library-objects')
        no_merge_library.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(no_merge_library)

        """No merges for string constants."""
        no_merges = self.make_binary_option('no-merges')
        no_merges.set_more_precise_than('TRUE', 'FALSE')
        # TODO: Constraint between this and distinguish-all-string-buffers?
        doop.add_option(no_merges)

        """Symbolic reasoning for expressions"""
        symbolic_reasoning = self.make_binary_option('symbolic-reasoning')
        # TODO: Partial order?
        doop.add_option(symbolic_reasoning)

        """Allow data-flow logic to go into library code using CHA."""
        data_flow_lib = self.make_binary_option('data-flow-goto-lib')
        data_flow_lib.set_more_sound_than('TRUE', 'FALSE')
        # TODO: Constraint, only on data-flow analysis.
        doop.add_option(symbolic_reasoning)

        """Run data-flow logic """
        data_flow_only_lib = self.make_binary_option('data-flow-only-lib')
        data_flow_only_lib.set_more_sound_than('FALSE', 'TRUE')
        # TODO: Constraint, only on data-flow analysis.
        doop.add_option(data_flow_only_lib)

        """Extract more string constants from the input code (may degrade performance)"""
        extract_more_strings = self.make_binary_option('extract-more-strings')
        extract_more_strings.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(extract_more_strings)

        """Do not model string values uniquely in a memory dump."""
        heapdl_nostrings = self.make_binary_option('heapdl-nostrings')
        heapdl_nostrings.set_more_precise_than('FALSE', 'TRUE')
        doop.add_option(heapdl_nostrings)

        """Skip strings without enclosing function information"""
        only_precise_native_strings = self.make_binary_option('only-precise-native-strings')
        only_precise_native_strings.set_more_sound_than('FALSE', 'TRUE')
        doop.add_option(only_precise_native_strings)

        """Merge all string constants except those useful for reflection."""
        distinguish_reflection_string = self.make_binary_option('distinguish-reflection-only-string-constants')
        distinguish_reflection_string.set_more_precise_than('TRUE', 'FALSE')
        # TODO: Check this partial order. If the default behavior is to merge, then this is right.
        # TODO: Constraint between this and no-merge?
        doop.add_option(distinguish_reflection_string)

        """Merge string buffer objects only on a per-package basis"""
        distinguish_reflection_string_per_package = self.make_binary_option('distinguish-string-buffers-per-package')
        distinguish_reflection_string_per_package.set_more_precise_than('TRUE', 'FALSE')
        # TODO: Again, verify that the default behavior is to merge all string buffer objects.
        doop.add_option(distinguish_reflection_string_per_package)

        """Enable logic for handling Java reflection."""
        reflection = self.make_binary_option('reflection')
        reflection.set_more_sound_than('TRUE', 'FALSE')
        doop.add_option(reflection)

        """Enable (classic subset of) logic for handling Java reflection."""
        reflection_classic = self.make_binary_option('reflection-classic')
        reflection_classic.set_more_sound_than('TRUE', 'FALSE')
        doop.add_option(reflection_classic)

        """Enable handling of the Java dynamic proxy API."""
        reflection_dynamic_proxies = self.make_binary_option('reflection_dynamic_proxies')
        reflection_dynamic_proxies.set_more_sound_than('TRUE', 'FALSE')
        doop.add_option(reflection_dynamic_proxies)

        """Enable extra rules for more sound handling of refleciton."""
        reflection_high_soundness_mode = self.make_binary_option('reflection-high-soundness-mode')
        reflection_high_soundness_mode.set_more_sound_than('TRUE', 'FALSE')
        doop.add_option(reflection_high_soundness_mode)

        # TODO: There are four more reflection options whose function is not clear.
        # reflection-invent-unknown-objects: Reflection-based handling of the method handle APIs.
        # reflection-method-handles: Reflection-based handling of the method handle APIs.
        # reflection-refined-objects: Reflection-based handling of the method handle APIs.
        # reflection-speculative-use-based-analysis: Reflection-based handling of the method handle APIs.

        """Allows reasoning on what substrings may yield reflection objects."""
        reflection_substring_analysis = self.make_binary_option('reflection-substring-analysis')
        # TODO: What is the partial order here?
        doop.add_option(reflection_substring_analysis)

        """Enable precise generics pre-anaysis to infer content types for Collections and Maps."""
        generics_pre = self.make_binary_option('Xgenerics-pre')
        generics_pre.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(generics_pre)

        """Precise handling for maps and collections."""
        precise_generics = self.make_binary_option('Xprecise-generics')
        precise_generics.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(precise_generics)

        """Merge strings that will not conflict in reflection resolution."""
        reflection_coloring = self.make_binary_option('Xreflection-coloring')
        reflection_coloring.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(reflection_coloring)

        """Enable context-sensitive handling of reflection."""
        reflection_context_sensitivity = self.make_binary_option('Xreflection-context-sensitivity')
        reflection_context_sensitivity.set_more_precise_than('TRUE', 'FALSE')
        doop.add_option(reflection_context_sensitivity)

        return doop