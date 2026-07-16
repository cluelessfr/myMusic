(() => {
    let activeCollectionUri = null;

    function isSpicetifyReady() {
        return Boolean(
            window.Spicetify?.ContextMenu &&
            window.Spicetify?.Locale &&
            window.Spicetify?.Platform?.History &&
            window.Spicetify?.showNotification
        );
    }

    function spotifyUriFromPath(pathname) {
        if (typeof pathname !== "string") {
            return null;
        }

        const splitUrl = pathname.split("/");
        const id = splitUrl[2];
        const type = splitUrl[1];
        const validTypes = ["album", "playlist"];

        if (!/^[A-Za-z0-9]{22}$/.test(id)) {
            return null;
        }

        if (!validTypes.includes(type)) {
            return null;
        }

        return `spotify:${type}:${id}`;
    }

    function isSingleDownloadableSelection(uris) {
        activeCollectionUri = null;

        if (!Array.isArray(uris) || uris.length !== 1) {
            return false;
        }

        const selectedUri = uris[0];

        if (typeof selectedUri !== "string") {
            return false;
        }

        if (selectedUri.startsWith("spotify:track:")) {
            return true;
        }

        else if (selectedUri.startsWith("spotify:playlist:") || selectedUri.startsWith("spotify:album:")) {
            activeCollectionUri = selectedUri;
            return false;
        }

        return false;
    }

    function findNativeDownloadMenuItem(target) {
        if (activeCollectionUri === null) {
            return null;
        }

        if (!(target instanceof Element)) {
            return null;
        }

        const closestButton = target.closest('button[role="menuitemcheckbox"]');

        if (!closestButton) {
            return null;
        }

        const buttonText = closestButton.textContent.trim();

        if (closestButton.dataset.mymusicDownload !== "true") {
            return null;
        }

        const downloadText = Spicetify.Locale.get("contextmenu.download");

        if (typeof downloadText !== "string") {
            return null;
        }

        if (buttonText !== downloadText.trim()) {
            return null;
        }

        return closestButton;
    }

    function enableNativeDownloadMenuItem() {
        if (typeof activeCollectionUri !== "string") {
            return;
        }

        if (!(activeCollectionUri.startsWith("spotify:playlist:") || activeCollectionUri.startsWith("spotify:album:"))) {
            return;
        }

        const downloadText = Spicetify.Locale.get("contextmenu.download");

        if (typeof downloadText !== "string") {
            return;
        }

        const menuItems = document.querySelectorAll('button[role="menuitemcheckbox"][aria-disabled="true"]');
        const array = Array.from(menuItems);

        const downloadButton = array.find(button => button.textContent.trim() === downloadText.trim());

        if (!downloadButton) {
            return;
        }

        const surroundingMenu = downloadButton.closest('[role="menu"]');

        if (!surroundingMenu) {
            return;
        }

        const enabledButton = surroundingMenu.querySelector('button[role^="menuitem"]:not([aria-disabled="true"])');

        if (!enabledButton) {
            return;
        }

        downloadButton.className = enabledButton.className;
        downloadButton.dataset.mymusicDownload = "true";
        downloadButton.setAttribute("aria-disabled", "false");
        downloadButton.tabIndex = 0;
    }

    function handleMenuMutations(mutationRecords) {
        for (const mutation of mutationRecords) {
            for (const node of mutation.addedNodes) {
                if (!(node instanceof Element)) {
                    continue;
                }

                if (!(node.closest('[role="menu"]') || node.querySelector('[role="menu"]'))) {
                    continue;
                }

                enableNativeDownloadMenuItem();

                return;
            }
        }
    }

    function observeContextMenus() {
        const observer = new MutationObserver(handleMenuMutations);
        observer.observe(document.body, {childList: true, subtree: true});
    }

    function handleDownload(uris) {
        const selectedUri = uris[0];

        console.log("[myMusic] Selected Spotify URI: ", selectedUri);
        Spicetify.showNotification(`[myMusic] Selected ${selectedUri}`);
    }

    function handleNativeDownloadClick(event) {
        const nativeDownloadItem = findNativeDownloadMenuItem(event.target);

        if (nativeDownloadItem === null) {
            return;
        }

        const selectedUri = activeCollectionUri;

        if (typeof selectedUri !== "string") {
            return;
        }

        if (!(selectedUri.startsWith("spotify:playlist:") || selectedUri.startsWith("spotify:album:"))) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        handleDownload([selectedUri]);
        closeContextMenu(nativeDownloadItem);
    }

    function closeContextMenu(menuItem) {
        if (!(menuItem instanceof Element)) {
            return;
        }

        if (!menuItem.isConnected) {
            return;
        }

        if (menuItem.dataset.mymusicDownload !== "true") {
            return;
        }

        if (!menuItem.closest('[role="menu"]')) {
            return;
        }

        const escapeEvent = new KeyboardEvent("keydown", {key: "Escape", code: "Escape", bubbles: true, cancelable: true, composed: true});

        menuItem.dispatchEvent(escapeEvent);
    }

    function registerDownloadMenu() {
        const downloadItem = new Spicetify.ContextMenu.Item(
            "Download",
            handleDownload,
            isSingleDownloadableSelection,
            "download"
        );

        downloadItem.register();
    }

    function initialize() {
        if (window.__myMusicIntegrationLoaded) {
            return;
        }

        registerDownloadMenu();
        observeContextMenus();
        document.addEventListener("click", handleNativeDownloadClick, true);
        window.__myMusicIntegrationLoaded = true;
        console.log("[myMusic] Spotify integration initialized");
    }

    function waitForSpicetify() {
        if (!isSpicetifyReady()) {
            setTimeout(waitForSpicetify, 250);
            return;
        }

        initialize();
    }

    if (window.__myMusicIntegrationLoaded) {
        return;
    }

    waitForSpicetify();

})();