# Master Tables
from app.models.states import State
from app.models.districts import District
from app.models.blocks import Block
from app.models.villages import Village
from app.models.panchayats import Panchayat

from app.models.territory import TerritoryJoin

# # Census Masters
from app.models.population import Population
from app.models.livestocks import Livestock
from app.models.lulc import LULC
from app.models.crops import Crop
from app.models.waterbody import WaterbodyType
from app.models.industries import Industry

# Census Data Tables
from app.models.livestocks_census import LivestockCensus
from app.models.crop_census import CropCensus
from app.models.population_census import PopulationCensus
from app.models.waterbody_census import WaterbodyCensus
from app.models.lulc_census import LULCCensus
from app.models.groundwater_extraction import GroundwaterExtraction
from app.models.rainfall import Rainfall
from app.models.strange_table import StrangeTable


# Block Data Tables
from app.models.block_territory import BlockTerritory
from app.models.block_livestocks import BlockLivestock
from app.models.block_pop import BlockPop
from app.models.block_crops import BlockCrop
from app.models.block_industries import BlockIndustry
from app.models.block_ground import BlockGround
from app.models.block_lulc import BlockLULC
from app.models.budget_entities import BudgetEntity


from app.models.block_rainfall import BlockRainfall
from app.models.block_transfer_type import BlockTransferType
from app.models.block_transfer_sector import BlockTransferSector
from app.models.block_transfer import BlockWaterTransfer
from app.models.block_progress import BlockProgress
from app.models.block_category import BlockCategory


# Auth Tables
from app.models.users import User
from app.models.tickets import Ticket