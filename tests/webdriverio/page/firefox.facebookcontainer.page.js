/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

'use strict';

const { $ } = require('@wdio/globals');
const Page = require('./page');

/**
 * sub page containing specific selectors and methods for a specific page
 */
class FirefoxFacebookContainerPage extends Page {
    get firefoxDownloadLink() {
        return $('#download-firefox-cta');
    }

    get extensionLink() {
        return $('.extension-cta .mzp-c-cta-link');
    }

    /**
     * overwrite specific options to adapt it to page object
     */
    open() {
        return super.open('en-US/firefox/facebookcontainer/');
    }
}

module.exports = new FirefoxFacebookContainerPage();
