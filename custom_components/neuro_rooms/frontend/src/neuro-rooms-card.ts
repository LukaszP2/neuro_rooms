import { LitElement, html, css } from 'lit';
import { property, state } from 'lit/decorators.js';

export class NeuroRoomsCard extends LitElement {
  @property({ attribute: false }) public hass!: any;
  @property({ attribute: false }) public config!: any;

  @state() private _floors: any[] = [];
  @state() private _areas: any[] = [];
  @state() private _dataLoaded = false;

  static styles = css`
    ha-card {
      padding: 16px;
    }
    .header {
      font-size: 1.2rem;
      font-weight: bold;
      margin-bottom: 16px;
    }
    .floor {
      margin-bottom: 24px;
    }
    .floor-name {
      font-size: 1.1rem;
      font-weight: 500;
      border-bottom: 1px solid var(--divider-color, #ccc);
      padding-bottom: 4px;
      margin-bottom: 12px;
      color: var(--primary-color);
    }
    .areas {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }
    .room-card {
      border: 1px solid var(--divider-color, #ccc);
      border-radius: 8px;
      padding: 12px;
      background: var(--card-background-color, #fff);
    }
    .room-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .room-name {
      font-weight: 600;
    }
    .room-state {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
      text-transform: uppercase;
    }
    .room-state.idle { background: var(--label-badge-grey, #9e9e9e); }
    .room-state.occupied { background: var(--label-badge-red, #f44336); }
    .room-state.night { background: var(--label-badge-blue, #03a9f4); }
    .room-state.away { background: var(--label-badge-yellow, #ffeb3b); color: black; }
    
    .room-details {
      font-size: 0.85rem;
      color: var(--secondary-text-color);
    }
    .room-details pre {
      background: var(--secondary-background-color);
      padding: 8px;
      border-radius: 4px;
      overflow-x: auto;
      margin-top: 8px;
      font-size: 0.75rem;
    }
  `;

  setConfig(config: any) {
    this.config = config;
  }

  async updated(changedProps: Map<string | number | symbol, unknown>) {
    super.updated(changedProps);
    if (changedProps.has('hass') && this.hass && !this._dataLoaded) {
      this._dataLoaded = true;
      try {
        this._floors = await this.hass.callWS({ type: 'config/floor_registry/list' });
        this._areas = await this.hass.callWS({ type: 'config/area_registry/list' });
      } catch (err) {
        console.error("Neuro Rooms: Failed to fetch floors/areas", err);
      }
    }
  }

  getStubLayout() {
    // Collect all neuro room sensors by checking for our unique attribute
    const sensors = Object.values(this.hass.states).filter((stateObj: any) =>
      stateObj.entity_id.startsWith('sensor.') && stateObj.attributes.room_config !== undefined
    );

    // Map sensors to areas via device_registry if possible, but our sensors don't have area_id directly on state
    // Actually, HA state objects don't expose area_id or device_id directly. We need device/entity registry.
    // However, we put `room_config` in extra_state_attributes!
    
    const areaIdToSensors = new Map();
    const unassignedRooms: any[] = [];

    sensors.forEach((s: any) => {
      const config = s.attributes.room_config || {};
      const areaId = config.area_id;
      
      if (areaId) {
        if (!areaIdToSensors.has(areaId)) {
          areaIdToSensors.set(areaId, []);
        }
        areaIdToSensors.get(areaId).push(s);
      } else {
        unassignedRooms.push(s);
      }
    });

    // Group areas by floor, respecting _areas array order
    const floorsWithAreas = new Map();
    const unassignedAreas: any[] = [];

    this._areas.forEach(areaInfo => {
      const sensorsInArea = areaIdToSensors.get(areaInfo.area_id);
      if (sensorsInArea) {
        if (areaInfo.floor_id) {
          if (!floorsWithAreas.has(areaInfo.floor_id)) {
            floorsWithAreas.set(areaInfo.floor_id, []);
          }
          floorsWithAreas.get(areaInfo.floor_id).push({ area: areaInfo, rooms: sensorsInArea });
        } else {
          unassignedAreas.push({ area: areaInfo, rooms: sensorsInArea });
        }
      }
    });

    // Filter floors that have neuro rooms, strictly preserving _floors array order
    const sortedFloors = this._floors.filter(f => floorsWithAreas.has(f.floor_id));

    return { sortedFloors, floorsWithAreas, unassignedAreas, unassignedRooms };
  }

  render() {
    if (!this.hass || !this._dataLoaded) return html`<ha-card><div style="padding:16px;">Loading...</div></ha-card>`;

    const { sortedFloors, floorsWithAreas, unassignedAreas, unassignedRooms } = this.getStubLayout();

    return html`
      <ha-card>
        <div class="header">Neuro Rooms</div>
        
        ${sortedFloors.map(floor => html`
          <div class="floor">
            <div class="floor-name">${floor.name}</div>
            <div class="areas">
              ${floorsWithAreas.get(floor.floor_id).map((group: any) => this.renderAreaGroup(group))}
            </div>
          </div>
        `)}

        ${unassignedAreas.length > 0 ? html`
          <div class="floor">
            <div class="floor-name">Unassigned Areas</div>
            <div class="areas">
              ${unassignedAreas.map(group => this.renderAreaGroup(group))}
            </div>
          </div>
        ` : ''}

        ${unassignedRooms.length > 0 ? html`
          <div class="floor">
            <div class="floor-name">Unassigned Rooms</div>
            <div class="areas">
              ${unassignedRooms.map(room => this.renderRoom(room))}
            </div>
          </div>
        ` : ''}
      </ha-card>
    `;
  }

  renderAreaGroup(group: any) {
    // If multiple neuro rooms per area, list them all. Usually it's 1 area = 1 neuro room
    return html`
      ${group.rooms.map((room: any) => this.renderRoom(room, group.area.name))}
    `;
  }

  renderRoom(roomState: any, areaName?: string) {
    const config = roomState.attributes.room_config || {};
    const name = config.name || areaName || roomState.attributes.room_id || 'Unknown Room';
    const stateVal = roomState.state;
    
    // Cleanup config for display
    const displayAttrs = { ...roomState.attributes };
    delete displayAttrs.friendly_name;
    delete displayAttrs.icon;

    return html`
      <div class="room-card">
        <div class="room-header">
          <div class="room-name">${name}</div>
          <div class="room-state ${stateVal}">${stateVal}</div>
        </div>
        <div class="room-details">
          <details>
            <summary>Parameters / State</summary>
            <pre>${JSON.stringify(displayAttrs, null, 2)}</pre>
          </details>
        </div>
      </div>
    `;
  }
}

customElements.define('neuro-rooms-card', NeuroRoomsCard);

(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "neuro-rooms-card",
  name: "Neuro Rooms Card",
  description: "Displays hierarchy of floors and neuro rooms"
});

