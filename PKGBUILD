# Maintainer: Chris Down <iofc.org@christopher.down>

pkgname=yturl
pkgver=1.0
pkgrel=1
pkgdesc='A simple YouTube URL grabber.'
arch=('any')
url="https://github.com/cdown/${pkgname}"
license=('BSD')
depends=('python2')
source=("http://fakkelbrigade.eu/chris/software/${pkgname}/${pkgname}-${pkgver}.tar.gz")
md5sums=()

package() {
	install -d "${pkgdir}/usr/"{bin/,share/man/man1/}
	install -m755 "${srcdir}/${pkgname}-${pkgver}/${pkgname}" \
                  "${pkgdir}/usr/bin/${pkgname}"
	install -m755 "${srcdir}/${pkgname}-${pkgver}/${pkgname}.1" \
                  "${pkgdir}/share/man/man1/${pkgname}.1"
}
