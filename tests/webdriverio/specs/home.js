/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

'use strict';

const { expect } = require('@wdio/globals');
const HomePage = require('../page/home.page');

describe('Home Page', () => {
    it('should successfully sign for a newsletter', async () => {
        await HomePage.open();
        await HomePage.newsletterSignup('success@example.com');
        await expect(HomePage.newsletterForm).not.toBeDisplayed();
        await expect(HomePage.newsletterThanksMessage).toBeDisplayed();
    });
});
