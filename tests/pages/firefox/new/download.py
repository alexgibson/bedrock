# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import BasePage
from pages.regions.modal import ModalProtocol


class DownloadPage(BasePage):

    URL_TEMPLATE = '/{locale}/firefox/new/{params}'

    _download_button_locator = (By.CSS_SELECTOR, '#download-button-thanks > .download-link')
    _platforms_modal_link_locator = (By.CLASS_NAME, 'js-platform-modal-button')
    _platforms_modal_content_locator = (By.CLASS_NAME, 'mzp-u-modal-content')
    _join_firefox_modal_content_locator = (By.CLASS_NAME, 'join-firefox-content')

    @property
    def is_download_button_displayed(self):
        return self.is_element_displayed(*self._download_button_locator)

    def download_firefox(self):
        self.find_element(*self._download_button_locator).click()
        from pages.firefox.new.thank_you import ThankYouPage
        return ThankYouPage(self.selenium, self.base_url).wait_for_page_to_load()

    def open_other_platforms_modal(self):
        modal = ModalProtocol(self)
        self.find_element(*self._platforms_modal_link_locator).click()
        self.wait.until(lambda s: modal.displays(self._platforms_modal_content_locator))
        return modal

    def open_join_firefox_modal(self):
        modal = ModalProtocol(self)
        self.find_element(*self._download_button_locator).click()
        self.wait.until(lambda s: modal.displays(self._join_firefox_modal_content_locator))
        return modal
