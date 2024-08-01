""" For setting the post processing options. """
# clean
from enum import IntEnum


class PostProcessingOptions(IntEnum):

    """Enum class for enabling / disabling parts of the post processing."""

    PLOT_LINE = 1
    PLOT_CARPET = 2
    PLOT_SANKEY = 3
    PLOT_SINGLE_DAYS = 4
    PLOT_MONTHLY_BAR_CHARTS = 5
    OPEN_DIRECTORY_IN_EXPLORER = 6
    EXPORT_TO_CSV = 7
    MAKE_NETWORK_CHARTS = 8
    GENERATE_PDF_REPORT = 9
    WRITE_COMPONENTS_TO_REPORT = 10
    WRITE_ALL_OUTPUTS_TO_REPORT = 11
    WRITE_NETWORK_CHARTS_TO_REPORT = 12
    PLOT_SPECIAL_TESTING_SINGLE_DAY = 13
    GENERATE_CSV_FOR_HOUSING_DATA_BASE = 14
    INCLUDE_CONFIGS_IN_PDF_REPORT = 15
    INCLUDE_IMAGES_IN_PDF_REPORT = 16
    PROVIDE_DETAILED_ITERATION_LOGGING = 17
    COMPUTE_OPEX = 18
    COMPUTE_CAPEX = 19
    COMPUTE_KPIS_AND_WRITE_TO_REPORT = 20
    PREPARE_OUTPUTS_FOR_SCENARIO_EVALUATION = 21
    MAKE_RESULT_JSON_FOR_WEBTOOL = 22
    WRITE_COMPONENT_CONFIGS_TO_JSON = 23
    WRITE_KPIS_TO_JSON_FOR_BUILDING_SIZER = 24
    WRITE_KPIS_TO_JSON = 25
    WRITE_ALL_KPIS_TO_JSON = 26
    MAKE_OPERATION_RESULTS_FOR_WEBTOOL = 27
