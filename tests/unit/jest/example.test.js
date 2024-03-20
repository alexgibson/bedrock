/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

/* global page, browser */

import 'expect-puppeteer';

describe('Home page', () => {
    beforeEach(async () => {
        await page.goto('https://www.mozilla.org/en-US/');
        const browserName = (await browser.version()).toLocaleLowerCase();

        if (browserName.includes('firefox')) {
            // console.log(browserName);
        }
    });

    it('should successfully sign up for a newsletter', async () => {
        await expect(page).toFill('#id_email', 'success@example.com');
        await expect(page).toClick('#privacy');
        await expect(page).toClick('#newsletter-submit');
        await expect(page).toMatchElement('#newsletter-thanks', {
            visible: true
        });
        await expect(page).toMatchElement('#newsletter-errors', {
            visible: false
        });
    });

    it('should show an error for newsletter form failure', async () => {
        await expect(page).toFill('#id_email', 'failure@example.com');
        await expect(page).toClick('#privacy');
        await expect(page).toClick('#newsletter-submit');
        await expect(page).toMatchElement('#newsletter-thanks', {
            visible: false
        });
        await expect(page).toMatchElement('#newsletter-errors', {
            visible: true
        });
    });
});
