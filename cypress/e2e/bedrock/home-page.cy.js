/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

describe('The Home Page', () => {
    beforeEach(() => {
        cy.visit('/en-US/');
    });

    it('should successfully signs up for a newsletter', () => {
        const email = 'success@example.com';
        cy.get('#id_email').type(`${email}{enter}`);
        cy.get('#privacy').check();
        cy.get('#newsletter-submit').click();
        cy.get('#newsletter-thanks').should('be.visible');
    });

    it('should handle newsletter error', () => {
        const email = 'failure@example.com';
        cy.get('#id_email').type(`${email}{enter}`);
        cy.get('#privacy').check();
        cy.get('#newsletter-submit').click();
        cy.get('#newsletter-errors').should('be.visible');
    });
});
