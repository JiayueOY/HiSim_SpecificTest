"""  Household system setup with only heatpump and without PV system. """
# clean
from typing import Optional, Any
from dataclasses import dataclass
from pathlib import Path
from dataclasses_json import dataclass_json
from utspclient.helpers.lpgdata import (
    ChargingStationSets,
    Households,
    TransportationDeviceSets,
    TravelRouteSets,
    EnergyIntensityType,
)
from utspclient.helpers.lpgpythonbindings import JsonReference
from hisim.simulator import SimulationParameters
from hisim.components import loadprofilegenerator_utsp_connector
from hisim.components import weather
from hisim.components import building
from hisim.components import generic_heat_pump
from hisim.components import electricity_meter
from hisim.utils import get_environment_variable
from hisim import log

__authors__ = "Vitor Hugo Bellotto Zago, Noah Pflugradt"
__copyright__ = "Copyright 2022, FZJ-IEK-3"
__credits__ = ["Noah Pflugradt"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Noah Pflugradt"
__status__ = "development"


@dataclass_json
@dataclass
class HouseholdConfig:

    """Configuration for Household."""


    building_type: str
    household_type: JsonReference
    energy_intensity: EnergyIntensityType
    result_path: str
    travel_route_set: JsonReference
    simulation_parameters: SimulationParameters
    data_acquisition_mode: loadprofilegenerator_utsp_connector.LpgDataAcquisitionMode
    transportation_device_set: JsonReference
    charging_station_set: JsonReference



    total_base_area_in_m2: float

    @classmethod
    def get_default(cls):
        """Get default HouseholdConfig."""

        return HouseholdConfig(

            building_type="blub",
            household_type=Households.CHR01_Couple_both_at_Work,
            energy_intensity=EnergyIntensityType.EnergySaving,
            data_acquisition_mode = loadprofilegenerator_utsp_connector.LpgDataAcquisitionMode.USE_UTSP,
            simulation_parameters=SimulationParameters.one_day_only(2022),
            result_path="HiSim/results",
            travel_route_set=TravelRouteSets.Travel_Route_Set_for_10km_Commuting_Distance,
            transportation_device_set=TransportationDeviceSets.Bus_and_one_30_km_h_Car,
            charging_station_set=ChargingStationSets.Charging_At_Home_with_11_kW,



            total_base_area_in_m2=121.2,
        )


def setup_function(
    my_sim: Any, my_simulation_parameters: Optional[SimulationParameters] = None
) -> None:  # noqa: too-many-statements
    """Basic household system setup.

    This setup function emulates a household with some basic components. Here the residents have their
    electricity and heating needs covered by the heat pump.

    - Simulation Parameters
    - Components
        - Occupancy (Residents' Demands)
        - Weather

        - Building
        - Heat Pump
    """

    config_filename = "hp_config.json"

    my_config: HouseholdConfig
    if Path(config_filename).is_file():
        with open(config_filename, encoding="utf8") as system_config_file:
            my_config = HouseholdConfig.from_json(system_config_file.read())  # type: ignore
        log.information(f"Read system config from {config_filename}")
    else:
        my_config = HouseholdConfig.get_default()

    # =================================================================================================================================
    # Set System Parameters

    # Set Simulation Parameters
    year = 2021
    seconds_per_timestep = 60

    # Set Occupancy
    data_acquisition_mode = my_config.data_acquisition_mode
    household = my_config.household_type
    energy_intensity = my_config.energy_intensity
    result_path = my_config.result_path
    travel_route_set = my_config.travel_route_set
    transportation_device_set = my_config.transportation_device_set
    charging_station_set = my_config.charging_station_set



    # Set Heat Pump Controller
    hp_mode = 2

    # =================================================================================================================================
    # Build Components

    # Build system parameters
    if my_simulation_parameters is None:
        my_simulation_parameters = SimulationParameters.january_only_with_customized_options(
            year=year, seconds_per_timestep=seconds_per_timestep
        )
    my_sim.set_simulation_parameters(my_simulation_parameters)

    # Build occupancy
    my_occupancy_config = loadprofilegenerator_utsp_connector.UtspLpgConnectorConfig(
        name="UTSPConnector",
        data_acquisition_mode=data_acquisition_mode,
        household=household,
        energy_intensity=energy_intensity,
        result_dir_path=result_path,
        travel_route_set=travel_route_set,
        transportation_device_set=transportation_device_set,
        charging_station_set=charging_station_set,
        consumption=0,
        profile_with_washing_machine_and_dishwasher=True,
        predictive_control=False,
        predictive=False,
    )

    my_occupancy = loadprofilegenerator_utsp_connector.UtspLpgConnector(
        config=my_occupancy_config, my_simulation_parameters=my_simulation_parameters
    )

    # Build Weather
    my_weather = weather.Weather(
        config=weather.WeatherConfig.get_default(weather.LocationEnum.GB),
        my_simulation_parameters=my_simulation_parameters,
    )



    # Build Electricity Meter
    my_electricity_meter = electricity_meter.ElectricityMeter(
        my_simulation_parameters=my_simulation_parameters,
        config=electricity_meter.ElectricityMeterConfig.get_electricity_meter_default_config(),
    )

    # Build Building
    my_building = building.Building(
        config=building.BuildingConfig.get_default_london_single_family_home(),
        my_simulation_parameters=my_simulation_parameters,
    )

    # Build Heat Pump Controller Config
    my_heat_pump_controller_config = (
        generic_heat_pump.GenericHeatPumpControllerConfig.get_default_generic_heat_pump_controller_config()
    )
    my_heat_pump_controller_config.mode = hp_mode

    # Build Heat Pump Controller
    my_heat_pump_controller = generic_heat_pump.GenericHeatPumpController(
        config=my_heat_pump_controller_config,
        my_simulation_parameters=my_simulation_parameters,
    )

    # Build Heat Pump
    my_heat_pump = generic_heat_pump.GenericHeatPump(
        config=generic_heat_pump.GenericHeatPumpConfig.get_default_generic_heat_pump_config(),
        my_simulation_parameters=my_simulation_parameters,
    )

    # =================================================================================================================================
    # # Connect Component Inputs with Outputs

    my_building.connect_input(
        my_building.ThermalPowerDelivered,
        my_heat_pump.component_name,
        my_heat_pump.ThermalPowerDelivered,
    )

    # =================================================================================================================================
    # Add Components to Simulation Parameters

    my_sim.add_component(my_occupancy)
    my_sim.add_component(my_weather)

    my_sim.add_component(my_electricity_meter, connect_automatically=True)
    my_sim.add_component(my_building, connect_automatically=True)
    my_sim.add_component(my_heat_pump_controller, connect_automatically=True)
    my_sim.add_component(my_heat_pump, connect_automatically=True)
