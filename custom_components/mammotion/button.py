"""Mammotion button sensor entities."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MammotionConfigEntry
from .coordinator import MammotionBaseUpdateCoordinator
from .entity import MammotionBaseEntity


@dataclass(frozen=True, kw_only=True)
class MammotionButtonSensorEntityDescription(ButtonEntityDescription):
    """Describes Mammotion button sensor entity."""

    press_fn: Callable[[MammotionBaseUpdateCoordinator], Awaitable[None]]


BUTTON_SENSORS: tuple[MammotionButtonSensorEntityDescription, ...] = (
    MammotionButtonSensorEntityDescription(
        key="start_map_sync",
        press_fn=lambda coordinator: coordinator.async_sync_maps(),
        entity_category=EntityCategory.CONFIG,
    ),
    MammotionButtonSensorEntityDescription(
        key="resync_rtk_dock",
        press_fn=lambda coordinator: coordinator.async_rtk_dock_location(),
        entity_category=EntityCategory.CONFIG,
    ),
    MammotionButtonSensorEntityDescription(
        key="release_from_dock",
        press_fn=lambda coordinator: coordinator.async_leave_dock(),
    ),
    MammotionButtonSensorEntityDescription(
        key="emergency_nudge_forward",
        press_fn=lambda coordinator: coordinator.async_move_forward(0.4),
    ),
    MammotionButtonSensorEntityDescription(
        key="emergency_nudge_left",
        press_fn=lambda coordinator: coordinator.async_move_left(0.4),
    ),
    MammotionButtonSensorEntityDescription(
        key="emergency_nudge_right",
        press_fn=lambda coordinator: coordinator.async_move_right(0.4),
    ),
    MammotionButtonSensorEntityDescription(
        key="emergency_nudge_back",
        press_fn=lambda coordinator: coordinator.async_move_back(0.4),
    ),
    MammotionButtonSensorEntityDescription(
        key="cancel_task",
        press_fn=lambda coordinator: coordinator.async_cancel_task(),
    ),
    MammotionButtonSensorEntityDescription(
        key="clear_all_mapdata",
        press_fn=lambda coordinator: coordinator.clear_all_maps(),
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MammotionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mammotion button sensor entity."""
    mammotion_devices = entry.runtime_data

    for mower in mammotion_devices:
        async_add_entities(
            MammotionButtonSensorEntity(mower.reporting_coordinator, entity_description)
            for entity_description in BUTTON_SENSORS
        )


class MammotionButtonSensorEntity(MammotionBaseEntity, ButtonEntity):
    """Mammotion button sensor entity."""

    entity_description: MammotionButtonSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MammotionBaseUpdateCoordinator,
        entity_description: MammotionButtonSensorEntityDescription,
    ) -> None:
        """Initialize the button sensor entity."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator)
