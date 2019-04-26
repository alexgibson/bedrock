/* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function() {
    'use strict';

    var helpButton = document.querySelector('.c-button-help');
    var helpContent = document.getElementById('browser-help');
    var helpTitle = helpContent.querySelector('.c-modal-title');

    helpButton.addEventListener('click', function(e) {
        e.preventDefault();

        Mzp.Modal.createModal(e.target, helpContent, {
            title: helpTitle.innerHTML,
            className: 'mzp-t-firefox l-compact',
            closeText: window.Mozilla.Utils.trans('global-close'),
        });

        window.dataLayer.push({
            'event': 'in-page-interaction',
            'eAction': 'link click',
            'eLabel': 'Browser help click'
        });
    }, false);

})();
