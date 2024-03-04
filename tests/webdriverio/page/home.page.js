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
class HomePage extends Page {
    get newsletterForm() {
        return $('#newsletter-form');
    }

    get newsletterThanksMessage() {
        return $('#newsletter-thanks');
    }

    get newsletterEmailInput() {
        return $('#id_email');
    }

    get newsletterPrivacyCheckbox() {
        return $('#privacy');
    }

    get newsletterSubmitButton() {
        return $('#newsletter-submit');
    }

    /**
     * a method to encapsule automation code to interact with the page
     * e.g. to login using username and password
     */
    async newsletterSignup(email) {
        await this.newsletterEmailInput.setValue(email);
        await this.newsletterPrivacyCheckbox.click();
        await this.newsletterSubmitButton.click();
    }

    /**
     * overwrite specific options to adapt it to page object
     */
    open() {
        return super.open('en-US/');
    }
}

module.exports = new HomePage();
