#define gitdate 20130515

#%if 0%{?fedora} >= 21
%define with_rdp 1
#%endif

%bcond_with rpi

%if %{with rpi}
%define with_rpi 1
%endif

Name:           weston
Version:        1.6.0
Release:        3%{?alphatag}%{?dist}
Summary:        Reference compositor for Wayland
Group:          User Interface/X
License:        BSD and CC-BY-SA
URL:            http://wayland.freedesktop.org/
%if 0%{?gitdate}
Source0:        %{name}-%{gitdate}.tar.bz2
%else
Source0:        http://wayland.freedesktop.org/releases/%{name}-%{version}.tar.xz
%endif
Source1:        make-git-snapshot.sh

# git diff-tree -p 1.0.6..origin/1.0 > weston-$(git describe origin/1.0).patch
#Patch0:		weston-1.0.5-11-g9a576c3.patch

BuildRequires:  autoconf
BuildRequires:  cairo-devel >= 1.10.0
BuildRequires:  glib2-devel
BuildRequires:  libdrm-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  librsvg2
BuildRequires:  libtool
BuildRequires:  libinput-devel
%if 0%{?fedora} < 18
BuildRequires:  libudev-devel
%endif
# libunwind available only on selected arches
%ifarch %{arm} aarch64 hppa ia64 mips ppc %{power64} %{ix86} x86_64
BuildRequires:	libunwind-devel
%endif
BuildRequires:  libva-devel
BuildRequires:  libwayland-client-devel
BuildRequires:  libwayland-server-devel >= 1.3.0
BuildRequires:  libwayland-cursor-devel
BuildRequires:  libwebp-devel
BuildRequires:  libxcb-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libxkbcommon-devel >= 0.1.0-8
BuildRequires:  mesa-libEGL-devel >= 8.1
BuildRequires:  mesa-libgbm-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  mesa-libwayland-egl-devel
BuildRequires:  mtdev-devel
BuildRequires:  pam-devel
BuildRequires:  pixman-devel
BuildRequires:  poppler-devel
BuildRequires:  poppler-glib-devel
BuildRequires:  systemd-devel
BuildRequires:  dbus-devel
BuildRequires:  lcms2-devel
BuildRequires:  colord-devel
%if 0%{?with_rdp}
BuildRequires:  freerdp-devel >= 1.1.0
%endif
%if 0%{with_rpi}
BuildRequires: pkgconfig(bcm_host)
Requires: raspberrypi-vc-libs
%endif
%description
Weston is the reference wayland compositor that can run on KMS, under X11
or under another compositor.

%package devel
Summary: Common headers for weston
License: MIT
Requires: %{name}%{?_isa} = %{version}-%{release}
%description devel
Common headers for weston

%prep
%setup -q -n %{name}-%{?gitdate:%{gitdate}}%{!?gitdate:%{version}}
#%patch0 -p1 -b .git

%build
# temporary force to pick up configure.ac changes
%if 1 || 0%{?gitdate}
autoreconf -ivf
%endif
%if %{with_rpi}
export WESTON_NATIVE_BACKEND="rpi-backend.so"
%endif

%configure \
	--disable-static --disable-setuid-install \
	%{?with_rdp:--enable-rdp-compositor} \
%if ! 0%{with_rpi}
	--enable-xwayland \
%endif
%if 0%{with_rpi}
	--disable-x11-compositor \
	--disable-drm-compositor \
	--disable-wayland-compositor \
	--enable-weston-launch \
	--disable-simple-egl-clients \
	--disable-egl \
	--disable-libunwind \
	--disable-colord \
	--disable-resize-optimization \
	--disable-xwayland-test \
	--with-cairo=image
%endif
	   
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT -name \*.la | xargs rm -f

%files
%doc README
%doc COPYING
%{_bindir}/weston
%{_bindir}/weston-info
%attr(4755,root,root) %{_bindir}/weston-launch
%{_bindir}/weston-terminal
%{_bindir}/wcap-decode
%dir %{_libdir}/weston
%{_libdir}/weston/cms-static.so
%{_libdir}/weston/desktop-shell.so
%{_libdir}/weston/fbdev-backend.so
%{_libdir}/weston/headless-backend.so
%{_libdir}/weston/xwayland.so
%{_libdir}/weston/fullscreen-shell.so
%if %{with_rdp}
%{_libdir}/weston/rdp-backend.so
%endif
%if %{with_rpi}
%{_libdir}/weston/rpi-backend.so
%endif
%{_libexecdir}/weston-*
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%dir %{_datadir}/weston
%{_datadir}/weston/*.png
%{_datadir}/weston/wayland.svg

%files devel
%dir %{_includedir}/weston
%{_includedir}/weston/compositor.h
%{_includedir}/weston/config-parser.h
%{_includedir}/weston/matrix.h
%{_includedir}/weston/version.h
%{_includedir}/weston/zalloc.h
%{_libdir}/pkgconfig/weston.pc

%changelog
* Sat Mar 28 2015 Kevin Ross <me@kevinross.name> - 1.6.0-3
- Update spec for Raspberry Pi 2

* Sun Sep 21 2014 Kalev Lember <kalevlember@gmail.com> - 1.6.0-2
- Enable webp and vaapi support
- Install weston-launch as setuid root (#1064023)

* Sun Sep 21 2014 Kalev Lember <kalevlember@gmail.com> - 1.6.0-1
- Update to 1.6.0
- Pull in the main package for -devel subpackage

* Fri Sep 12 2014 Peter Hutterer <peter.hutterer@redhat.com> - 1.5.91-2
- Rebuild for libinput soname bump

* Fri Aug 22 2014 Kevin Fenzi <kevin@scrye.com> 1.5.91-1
- Update to 1.5.91

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jul 19 2014 Kevin Fenzi <kevin@scrye.com> 1.5.0-6
- Rebuild for new libfreerdp

* Sun Jun 15 2014 Lubomir Rintel <lkundrak@v3.sk> - 1.5.0-5
- Enable DBus support so that logind integration actually works

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Dan Horák <dan[at]danny.cz> - 1.5.0-3
- libunwind available only on selected arches

* Wed May 21 2014 Richard Hughes <rhughes@redhat.com> - 1.5.0-1
- Weston 1.5.0

* Tue May 13 2014 Richard Hughes <rhughes@redhat.com> - 1.4.93-1
- Weston 1.4.93

* Mon Jan 27 2014 Adam Jackson <ajax@redhat.com> 1.4.0-2
- Rebuild for new sonames in libxcb 1.10

* Fri Jan 24 2014 Richard Hughes <rhughes@redhat.com> - 1.4.0-1
- Weston 1.4.0

* Mon Jan 20 2014 Richard Hughes <rhughes@redhat.com> - 1.3.93-1
- Weston 1.3.93

* Tue Dec 17 2013 Richard Hughes <rhughes@redhat.com> - 1.3.91-1
- Weston 1.3.91

* Mon Nov 25 2013 Lubomir Rintel <lkundrak@v3.sk> - 1.3.1-1
- Weston 1.3.1

* Thu Oct 03 2013 Adam Jackson <ajax@redhat.com> 1.2.0-3
- Build RDP backend if we have new enough freerdp (#991220)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed May 15 2013 Richard Hughes <rhughes@redhat.com> - 1.1.90-0.1.20130515
- Update to a git snapshot based on what will become 1.1.90

* Tue Apr 16 2013 Richard Hughes <richard@hughsie.com> 1.1.0-1
- weston 1.1.0

* Wed Mar 27 2013 Richard Hughes <richard@hughsie.com> 1.0.6-1
- weston 1.0.6

* Thu Feb 21 2013 Adam Jackson <ajax@redhat.com> 1.0.5-1
- weston 1.0.5+ (actually tip of 1.0 branch)

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 21 2013 Adam Tkac <atkac redhat com> - 1.0.3-2
- rebuild due to "jpeg8-ABI" feature drop

* Wed Jan 02 2013 Adam Jackson <ajax@redhat.com> 1.0.3-1
- weston 1.0.3

* Fri Dec 21 2012 Adam Tkac <atkac redhat com> - 1.0.0-2
- rebuild against new libjpeg

* Tue Oct 23 2012 Adam Jackson <ajax@redhat.com> 1.0.0-1
- weston 1.0.0

* Thu Oct 18 2012 Adam Jackson <ajax@redhat.com> 0.99.0-1
- weston 0.99.0

* Mon Sep 17 2012 Thorsten Leemhuis <fedora@leemhuis.info> 0.95.0-3
- add libXcursor-devel as BR

* Mon Sep 17 2012 Thorsten Leemhuis <fedora@leemhuis.info> 0.95.0-2
- rebuild

* Mon Sep 17 2012 Thorsten Leemhuis <fedora@leemhuis.info> 0.95.0-1
- Update to 0.95.0
- enable xwayland
- make it easier to switch between a release and a git snapshot in spec file

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.89-0.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 05 2012 Adam Jackson <ajax@redhat.com> 0.89-0.4
- Rebuild for new libudev
- Conditional buildreq for libudev-devel

* Wed Apr 25 2012 Richard Hughes <richard@hughsie.com> 0.89-0.3
- New package addressing Fedora package review concerns.

* Tue Apr 24 2012 Richard Hughes <richard@hughsie.com> 0.89-0.2
- Initial package for Fedora package review.
