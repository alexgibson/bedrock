'use strict';

/** @type {import('jest-environment-puppeteer').JestPuppeteerConfig} */
module.exports = {
    launch: {
        dumpio: true,
        headless: process.env.HEADLESS !== 'false',
        product: 'firefox'
    },
    browserContext: 'default'
};
