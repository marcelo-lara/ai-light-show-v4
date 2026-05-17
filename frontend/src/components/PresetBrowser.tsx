import React from 'react';
import type { ParameterSchema } from '../types/phase03';

interface PresetBrowserProps {
  selected_presets: Set<string>;
  presets: Array<{
    id: string;
    name: string;
    label: string;
    parameters: ParameterSchema[];
  }>;
  on_preset_change: (preset_id: string, parameter_name: string, value: unknown) => void;
}

/**
 * Epic 02.F6, 02.F13, 02.F25: Preset Browser & Schema-Driven Controls
 *
 * Shows one tab per selected preset with parameter controls.
 * Tabs are hidden for unselected presets.
 */
export const PresetBrowser: React.FC<PresetBrowserProps> = ({
  selected_presets,
  presets,
  on_preset_change,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {presets.map((preset) => {
        const isSelected = selected_presets.has(preset.id);

        if (!isSelected) {
          return null;
        }

        return (
          <div
            key={preset.id}
            style={{
              padding: '16px',
              borderBottom: '1px solid #ddd',
              backgroundColor: '#fff',
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: '12px', fontSize: '13px' }}>
              {preset.name}
            </h4>

            {/* Parameter Controls */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {preset.parameters.map((param) => (
                <ParameterControl
                  key={param.name}
                  parameter={param}
                  on_change={(value) => on_preset_change(preset.id, param.name, value)}
                />
              ))}
            </div>
          </div>
        );
      })}

      {selected_presets.size === 0 && (
        <div style={{ padding: '16px', color: '#999', fontSize: '12px' }}>
          No presets selected. Select presets from the Main tab.
        </div>
      )}
    </div>
  );
};

interface ParameterControlProps {
  parameter: ParameterSchema;
  on_change: (value: unknown) => void;
}

const ParameterControl: React.FC<ParameterControlProps> = ({ parameter, on_change }) => {
  const { name, label, type, default_value, constraint } = parameter;

  switch (type) {
    case 'float':
    case 'int':
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', minWidth: '80px' }}>{label}:</label>
          <input
            type="range"
            min={constraint?.min_value ?? 0}
            max={constraint?.max_value ?? 100}
            step={constraint?.step_size ?? 1}
            defaultValue={default_value as number}
            onChange={(e) => on_change(Number(e.target.value))}
            style={{ flex: 1 }}
          />
          <span style={{ fontSize: '11px', minWidth: '30px' }}>{default_value}</span>
        </div>
      );

    case 'boolean':
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <input
              type="checkbox"
              defaultChecked={default_value as boolean}
              onChange={(e) => on_change(e.target.checked)}
            />
            {label}
          </label>
        </div>
      );

    case 'choice':
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', minWidth: '80px' }}>{label}:</label>
          <select
            defaultValue={default_value as string}
            onChange={(e) => on_change(e.target.value)}
            style={{ flex: 1, padding: '4px', fontSize: '12px' }}
          >
            {constraint?.choices?.map((choice) => (
              <option key={choice} value={choice}>
                {choice}
              </option>
            ))}
          </select>
        </div>
      );

    case 'color':
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', minWidth: '80px' }}>{label}:</label>
          <input
            type="color"
            defaultValue={default_value as string}
            onChange={(e) => on_change(e.target.value)}
            style={{ width: '40px', height: '28px' }}
          />
        </div>
      );

    default:
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', minWidth: '80px' }}>{label}:</label>
          <input
            type="text"
            defaultValue={String(default_value)}
            onChange={(e) => on_change(e.target.value)}
            style={{ flex: 1, padding: '4px', fontSize: '12px' }}
          />
        </div>
      );
  }
};

export default PresetBrowser;
