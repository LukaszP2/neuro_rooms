import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: '../www',
    lib: {
      entry: 'src/neuro-rooms-card.ts',
      name: 'NeuroRoomsCard',
      formats: ['es'],
      fileName: () => 'neuro-rooms-card.js'
    }
  }
});
