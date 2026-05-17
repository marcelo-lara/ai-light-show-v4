import { describe, expect, it } from 'vitest';
import type {
    RenderArtifactMetadata,
    CurrentCanvasState,
    CurrentSongState,
    PlaybackState,
    CompatibilityErrorState,
} from '../types/renderContract';

describe('renderContract types', () => {
    it('matches the render artifact metadata contract', () => {
        const metadata: RenderArtifactMetadata = {
            schema_version: '1.0',
            render_id: 'render_abc123',
            preset_id: 'preset_1',
            preset_version: '1.0',
            seed: 42,
            song_id: 'song_1',
            analysis_id: 'analysis_1',
            fps: 30,
            duration: 60,
            frame_count: 1800,
        };

        expect(metadata.schema_version).toBe('1.0');
        expect(metadata.render_id).toBe('render_abc123');
    });

    it('supports an empty current canvas state', () => {
        const emptyCanvas: CurrentCanvasState = {
            song_id: 'song_1',
            is_empty: true,
        };

        expect(emptyCanvas.is_empty).toBe(true);
        expect(emptyCanvas.canvas_id).toBeUndefined();
    });

    it('nests canvas state under the current song state', () => {
        const songState: CurrentSongState = {
            song_id: 'song_1',
            current_canvas: {
                song_id: 'song_1',
                is_empty: true,
            },
        };

        expect(songState.current_canvas?.is_empty).toBe(true);
    });

    it('keeps compatibility error messages actionable', () => {
        const errorState: CompatibilityErrorState = {
            has_error: true,
            error_message: 'Unsupported schema version: 2.0',
            incompatible_render_id: 'render_xyz',
            suggested_action: 'Generate a new render with the current schema.',
        };

        expect(errorState.has_error).toBe(true);
        expect(errorState.error_message.toLowerCase()).toContain('schema');
    });

    it('models backend playback state with song ownership', () => {
        const playbackState: PlaybackState = {
            current_song: {
                song_id: 'song_1',
                current_canvas: {
                    song_id: 'song_1',
                    is_empty: false,
                    render_artifact: {
                        metadata: {
                            schema_version: '1.0',
                            render_id: 'render_1',
                            preset_id: 'preset_1',
                            preset_version: '1.0',
                            seed: 42,
                            song_id: 'song_1',
                            analysis_id: 'analysis_1',
                            fps: 30,
                            duration: 60,
                            frame_count: 1800,
                        },
                    },
                },
            },
            is_playing: false,
            playback_time: 0,
        };

        expect(playbackState.current_song?.song_id).toBe('song_1');
        expect(playbackState.is_playing).toBe(false);
    });
});
