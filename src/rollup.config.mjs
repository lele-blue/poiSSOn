import fsextra from "fs-extra"
const {removeSync} = fsextra;
import autoPreprocess from 'svelte-preprocess'
import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import svelte from 'rollup-plugin-svelte'
import livereload from 'rollup-plugin-livereload'
import typescript from '@rollup/plugin-typescript';

const production = process.env['NODE_ENV'] === 'production'


// clear previous builds
removeSync("../main/static/build")


export default {
    preserveEntrySignatures: false,
    input: [
        `src/main.js`
    ],
    output: {
        sourcemap: true,
        format: 'module',
        dir: "../main/static/build/out",
        chunkFileNames: `[name]${production && '-[hash]' || ''}.js`
    },
    plugins: [
        typescript(),
        svelte({
            preprocess: [
                autoPreprocess({
                    postcss: {
                        plugins: []
                    }
                })
            ]
        }),
        resolve({
            browser: true,
            dedupe: importee => !!importee.match(/svelte(\/|$)/)
        }),
        commonjs({extensions: ['.js', '.ts']}),
        production,
        !production && livereload("../main/static/build"), // refresh entire window when code is updated
    ],
    watch: {
        clearScreen: false
    }
}


