/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

'use strict';

const BrowserSyncPlugin = require('browser-sync-webpack-plugin');
const MergeIntoSingleFilePlugin = require('webpack-merge-and-include-globally');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const UglifyJs = require('uglify-js');
const path = require('path');
const staticBundles = require('./media/static-bundles.json');
const webpack = require('webpack');

const uglifyOptions = {
    ie8: true
};

function resolveBundles(fileList){
    return fileList.map((f) => {
        if (f.match(/^protocol\//)) {
            return `./node_modules/@mozilla-protocol/core/${f}`;
        }
        return path.resolve(__dirname, 'media', f);
    });
}

function compressJs(code) {
    if (process.env.NODE_ENV === 'production') {
        const min = UglifyJs.minify(code, uglifyOptions);
        return min.code;
    }
    return code;
}

function getBundleNames(bundleType) {
    return staticBundles[bundleType].map(bundle => {
        return `${bundle['name']}--${bundleType}`;
    });
}

function getBundles(bundleType) {
    return new Promise((resolve) => {
        const allFiles = {};
        staticBundles[bundleType].forEach(bundle => {
            const name = `${bundle['name']}--${bundleType}`;
            const files = resolveBundles(bundle['files']);
            allFiles[name] = files;
        });
        resolve(allFiles);
    });
}

// Keep a reference to watched JS files for MergeIntoSingleFilePlugin
const jsBundleNames = getBundleNames('js');

const jsConfig = {
    mode: process.env.NODE_ENV,
    entry: () => getBundles('js'),
    output: {
        filename: 'temp/[name].js',
        path: path.resolve(__dirname, 'assets/'),
        publicPath: '/media/',
    },
    watchOptions: {
        aggregateTimeout: 600,
        ignored: './node_modules/'
    },
    performance: {
        hints: 'warning'
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
        }),
        // JS bundles use global scope instead of require() for older browser compatibility.
        new MergeIntoSingleFilePlugin({
            files: staticBundles['js'].map((bundle) => {
                return {
                    src: resolveBundles(bundle['files']),
                    dest: code => {
                        const name = `js/${bundle['name']}.js`;
                        const _code = compressJs(code);
                        const obj = {};
                        obj[name] = _code;
                        return obj;
                    }
                };
            }),
            chunks: jsBundleNames
        })
    ]
};

const cssConfig = {
    mode: process.env.NODE_ENV,
    entry: () => getBundles('css'),
    output: {
        filename: 'temp/[name].js',
        path: path.resolve(__dirname, 'assets/'),
        publicPath: '/media/',
    },
    optimization: {
        minimizer: [new CssMinimizerPlugin({})],
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                include: path.resolve(__dirname, 'media'),
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            url: false
                        }
                    },
                    'sass-loader',
                ],
            },
        ],
    },
    watchOptions: {
        aggregateTimeout: 600,
        ignored: './node_modules/'
    },
    performance: {
        hints: 'warning'
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
        }),
        new MiniCssExtractPlugin({
            filename: ({ chunk }) => `css/${chunk.name.replace('--css', '')}.css`,
        })
    ]
};

if (process.env.NODE_ENV === 'development') {
    const browserSync = new BrowserSyncPlugin({
        port: 8000,
        proxy: process.env.BS_PROXY_URL || 'localhost:8080',
        open: false,
        notify: true,
        reloadDebounce: 1000,
        injectChanges: false,
        files: ['./bedrock/**/*.html'],
        ui: {
            port: 8001
        },
        serveStatic: [{
            route: './media',
            dir: './assets'
        }]
    });

    jsConfig.plugins.push(browserSync);
    cssConfig.plugins.push(browserSync);
}

module.exports = [jsConfig, cssConfig];
