#!/usr/bin/env bash
set -u

NEW_VERSION=$1

sed -i -e "s/^Version: .*/Version: ${NEW_VERSION}-1~actionless~zesty/" packaging/ubuntu/control
sed -i -e "s/^pkgver=.*/pkgver=${NEW_VERSION}/" packaging/arch/PKGBUILD
