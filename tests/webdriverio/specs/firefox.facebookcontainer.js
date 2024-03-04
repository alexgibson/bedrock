/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

'use strict';

const { expect, browser } = require('@wdio/globals');
const FirefoxFacebookContainerPage = require('../page/firefox.facebookcontainer.page');

describe('Firefox Facebook Container Page', () => {
    it('should display the appropriate hero CTA', async () => {
        await FirefoxFacebookContainerPage.open();

        if (browser.capabilities.browserName !== 'firefox') {
            await expect(
                FirefoxFacebookContainerPage.firefoxDownloadLink
            ).toBeDisplayed();
        } else {
            await expect(
                FirefoxFacebookContainerPage.extensionLink
            ).toBeDisplayed();
        }
    });
});
