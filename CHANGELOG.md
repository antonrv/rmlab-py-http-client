# Changelog

## 0.3.0 - (2022-04-01)

* Added cache to store credentials and endpoints.
* Internal clients access cached credentials if not provided their arguments.

## 0.2.0 - (2022-03-23)

* Type/value-safe layer to adapt to server-defined endpoints.
* Request arguments checks to capture errors in request construction.

## 0.1.4 - (2022-03-11)

* Bug fix (aiohttp session was not being closed in HTTPClientJWTRenewable)
* AsyncClient as a context manager, for interface uniformity.

## 0.1.3 - (2022-03-07)

* Update rmlab-errors version (in setup.cfg)

## 0.1.2 - (2022-03-07)

* Update rmlab-errors version

## 0.1.1 - (2022-03-07)

* Async operation poll/result endpoints defined at first response, not static

## 0.1.0 - (2022-03-07)

* First release
