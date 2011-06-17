# All My Etherpads

Etherpads are awesome, but they have a few problems:

* There's no easy way to keep track of all your Etherpads, especially across
  multiple servers.

* Sometimes an Etherpad server goes down.

* Accessing an Etherpad on a mobile device isn't fun because the site loads
  very slowly.

[All My Etherpads][] is a simple mobile Web app that solves these problems by
storing HTML versions of your Etherpads for offline viewing.

## Technical Details

The app consists entirely of static files, though it uses a cross-domain Ajax
API at etherpad-export.appspot.com to retrieve the contents of Etherpads. The
source code for that server is in the `etherpad-export-proxy` directory.

The app uses the [jQuery Mobile][] framework for its user interface, and
currently uses [DOM Storage][] for offline storage. The [application cache][]
feature of HTML5 is used to allow the app to be used while offline.

## Development

To start working on this app, enter the root directory of the repository and
run:

    python server.py --ignore-cache-manifests

Then point your browser to:

    http://localhost:8001/

The `--ignore-cache-manifests` option will ensure that all the changes to your
code take effect immediately, without the application cache getting in the
way.

Once you want to publish your changes on a website, though, you should make
sure the `cache.manifest` file has changed so that clients retrieve the latest
version of the code.

  [All My Etherpads]: http://toolness.github.com/all-my-etherpads/
  [jQuery Mobile]: http://jquerymobile.com/
  [DOM Storage]: https://developer.mozilla.org/en/dom/storage
  [application cache]: http://www.w3.org/TR/2008/WD-html5-20080122/#appcache
