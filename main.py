from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

import subprocess


class X11WindowSwitcherExtension(Extension):
    def __init__(self):
        # Check that wmctrl is installed
        import shutil

        # Check that we have wmctrl before continuing
        if shutil.which("wmctrl"):
            # We have wmctrl, hook up extension
            super(X11WindowSwitcherExtension, self).__init__()
            self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        else:
            # No wmctrl, so bail
            import logging

            logger = logging.getLogger(__name__)
            logger.error("Missing Dependency: wmctrl not found on $PATH")
            import sys

            sys.exit()


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()
        search = str(event.get_argument() or "").lower().strip()

        items = []

        # Get list of all windows, and process into a dictionary that looks like this:
        # {<window_id>: {ws: <workspace_id>, name: <window_name>}}
        result = subprocess.run(
            ['wmctrl -xl | awk \'{ if( $2 != "-1") {print $1","$3} }\''],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # equivalent to capture_output=True
            shell=True,
            universal_newlines=True,  # equivalent to text=True
        ).stdout.split("\n")

        w_list = []
        for w in result:
            if w == '':
                continue
            w = w.strip().split(",")
            wid = w[0]
            wdisplay = w[1].split('.')[-1]
            w_list.append([wid, wdisplay])

        for w_idx, window in w_list:
            if search == "" or search in window.lower():
                items.append(
                    ExtensionResultItem(
                        icon="images/window.svg",
                        name=window,
                        on_enter=RunScriptAction("wmctrl -ia {}".format(w_idx)),
                    )
                )

        return RenderResultListAction(items)


if __name__ == "__main__":
    X11WindowSwitcherExtension().run()
