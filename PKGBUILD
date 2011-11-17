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
md5sums=('8f5c966f90ffee4faa8153bcd74381af')

package() {
    install -d "${pkgdir}/usr/"{bin/,share/man/man1/}

    # Change the shebang to work on Arch. ex is part of core/vi, so we don't
    # need to list it as a dependency. Interesting that Arch fails to comply
    # with POSIX/SUS by not including ed by default.
    ex -s "${srcdir}/${pkgname}" << 'EOF'
1s/.*/#!\/usr\/bin\/env python2/g
w
EOF

    # Compress the manual page to save a small amount of space.
    gzip -9 "${srcdir}/${pkgname}.1"

    install -m755 \
        "${srcdir}/${pkgname}" \
        "${pkgdir}/usr/bin/${pkgname}"
    install -m755 \
        "${srcdir}/${pkgname}.1.gz" \
        "${pkgdir}/usr/share/man/man1/${pkgname}.1.gz"
}
