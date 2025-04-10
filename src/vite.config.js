import { svelte } from '@sveltejs/vite-plugin-svelte'
import routify from '@roxi/routify/vite-plugin'
import { defineConfig } from 'vite'
import { resolve } from 'path'
import postCssNesting from 'postcss-nesting'

const production = process.env.NODE_ENV === 'production'

export default defineConfig({
    base: production ? "/auth/static/build/client" : "/auth/go",
    build: {
        outDir: '../main/static/build/',
        emptyOutDir: true
    },
    clearScreen: false,
    resolve: { alias: { '@': resolve('src'), '@components': resolve('src/components') } },
    plugins: [
        routify({
            render: { ssr: false, ssg: false },
            routesDir: {default: 'src/routes'},
            extensions: ['.svelte']
        }),
        svelte({
            compilerOptions: {
                dev: !production,
                hydratable: false,
            },
            extensions: ['.svelte'],
        }),
    ],
    css: { postcss: { plugins: [postCssNesting()] } },
})
