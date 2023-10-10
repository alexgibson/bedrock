/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

'use strict';

const path = require('path');
const glob = require('glob');

module.exports = {
    entry: glob.sync('tests/unit/spec/newsletter/form-utils.js'),
    output: {
        filename: 'test.js',
        path: path.resolve(__dirname, 'dist')
    },
    plugins: [],
    resolve: {
        modules: [__dirname, 'src', 'node_modules'],
        extensions: ['*', '.js']
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: require.resolve('babel-loader')
            }
        ]
    }
};
