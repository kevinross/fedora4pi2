# Pick hard or soft binaries and libs
%ifarch armv7hl
%global sourcedir hardfp/opt/vc
%else
%global sourcedir opt/vc
%endif

# Non-source package - no debuginfo available.
#%global debug_package %{nil}

# actually, the date is the date packaged, not the commit date
%global commit_date  20150327
%global commit_short 3ef516e
%global commit_long  3ef516ebc3e26e84e5f590688b8ad62cef8e8baf

# userland tarball directory
%global commit_userland_date    20150327
%global commit_short_userland   7650bcb
%global commit_long_userland    7650bcbc9ba8f1c5e29be7726d184b31c2665c46
%global userland_tar ../../SOURCES/raspberrypi-userland-%{commit_short_userland}.tar.gz
%global userland   raspberrypi-userland-%{commit_short_userland}
%global userland_build raspberrypi-userland-%{commit_short_userland}/build


Name:           raspberrypi-vc
Version:        %{commit_date}git%{commit_short}
Release:        2.rpfr20

Summary:        VideoCore GPU libraries, utilities, and demos for Raspberry Pi

License:        Redistributable, with restrictions; see LICENSE.broadcom
URL:            https://github.com/raspberrypi
Source0:        https://github.com/raspberrypi/firmware/tarball/%{commit_long}
Source1:	%{?scl_prefix}libs.conf
Source2:	https://github.com/raspberrypi/userland/tarball/%{commit_long_userland}
# Tarball is of the corresponding git commit
Patch0:		    raspberrypi-vc-demo-source-path-fixup.patch
Patch1: 	    raspberrypi-vc-pkgconfig.patch

# Patch0 fixes up paths for relocation from /opt to system directories.
BuildRequires: cmake, gcc-c++

ExclusiveArch:	armv5tel armv6l armv6hl armv7hl

%description
Libraries, utilities and demos for the Raspberry Pi BCM2835 SOC GPU

#---------------------------

%package static
Summary:        Static libraries for accessing the Raspberry Pi GPU
Requires:       %{name}-libs

%description static
Static versions of libraries for accessing the BCM2835 VideoCore GPU
on the Raspberry Pi computer.

#---------------------------

%package libs
Summary:       Libraries for accessing the Raspberry Pi GPU
Requires:      %{name}-firmware = %{version}
Provides: libEGL.so
Provides: libGLESv1_CM.so
Provides: libGLESv2.so
Provides: libOpenVG.so
Provides: libWFC.so
Provides: libbcm_host.so
Provides: libdebug_sym.so
Provides: libmmal.so
Provides: libmmal_vc_client.so
Provides: libmmal_core.so
Provides: libmmal_util.so
Provides: libopenmaxil.so
Provides: libvchiq_arm.so
Provides: libvcos.so
Provides: libvcsm.so

%description libs
Shared libraries for accessing the BCM2835 VideoCore GPU 
on the Raspberry Pi computer.

#---------------------------

%package utils
Summary:        Utilities related to the Raspberry Pi GPU
Requires:       %{name}-libs = %{version}

%description utils
Utilities for using the BCM2835 VideoCore GPU on the 
Raspberry Pi computer.

#---------------------------

%package libs-devel
Summary:        Headers for libraries that access the Raspberry Pi GPU
Requires:       %{name}-libs = %{version}
License:        GPLv2+ and Freely redistributable, with restrictions; see LICENCE.broadcom and headers
Provides:	khrplatform.h
Provides:	egl.h
Provides:	eglext.h
Provides:	eglplatform.h
Provides:	gl2.h
Provides:	pkgconfig(bcm_host)

%description libs-devel
Header files for accessing the BCM2835 VideoCore GPU on 
the Raspberry Pi computer.

#---------------------------

%package demo-source
Summary:        Demo source for accessing the Raspberry Pi GPU
Requires:       %{name}-libs = %{version}
License:	ASL 2.0

%description demo-source
Demo source code for accessing the BCM2835 VideoCore GPU
on the Raspberry Pi computer.


#---------------------------

%package firmware
Summary:       GPU firmware for the Raspberry Pi computer
License:       Redistributable, with restrictions; see LICENSE.broadcom
Obsoletes:     raspberrypi-firmware
%description firmware
This package contains the GPU firmware for the Raspberry Pi BCM2835 SOC
including the kernel bootloader.


#===========================

%prep
%setup -q -n raspberrypi-firmware-%{commit_short}
%setup -q -D -T -a 2 -n raspberrypi-firmware-%{commit_short}

%patch0 -p1
%patch1 -p1 -d raspberrypi-userland-%{commit_short_userland}

%build
# Here are the commands to build from source
# pwd
# tar -xf %SOURCE2
rm -rf opt
cd %{userland}

#sed -i 's/if (DEFINED CMAKE_TOOLCHAIN_FILE)/if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)/g' makefiles/cmake/arm-linux.cmake
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=RELEASE ..
make %{?_smp_mflags} install DESTDIR=. >/tmp/build.log 2>/tmp/build.log.err

%install 
# Firmware in /boot (built from original source)
mkdir -p %{buildroot}/boot
cp -p -v boot/start* boot/fixup* boot/bootcode.bin %{buildroot}/boot
chmod a-x %{buildroot}/boot/*
# Libraries built from source code that was installed by buildme
# Change to directory where /opt/vc is installed by make
cd raspberrypi-userland-%{commit_short_userland}/build/opt/vc/
echo '/%{sourcedir}/lib -> /usr/lib'
mkdir -p              %{buildroot}/%{_libdir}/vc/
cp -R -p -v lib/* %{buildroot}/%{_libdir}/vc/
mv %{buildroot}/%{_libdir}/vc/pkgconfig %{buildroot}/%{_libdir}

#mv %{buildroot}/%{_libdir}/libEGL.so %{buildroot}/%{_libdir}/vc/
mkdir -p 		%{buildroot}%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/ld.so.conf.d/

install -p -c -m 644 %{SOURCE1} %{buildroot}%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/ld.so.conf.d/

echo '/%{sourcedir}/bin -> /usr/bin'
mkdir -p              %{buildroot}/%{_bindir}
cp -R -p -v bin/* %{buildroot}/%{_bindir}

echo '/%{sourcedir}/sbin -> /usr/sbin'
mkdir -p               %{buildroot}/%{_sbindir}
cp -R -p -v sbin/* %{buildroot}/%{_sbindir}

echo '/%{sourcedir}/include -> /usr/include/vc'
mkdir -p                  %{buildroot}/%{_includedir}/vc/
mkdir -p %{buildroot}/%{_includedir}/interface/vcos/
mkdir -p %{buildroot}/%{_includedir}/interface/vmcs_host/
cp -R -p -v include/* %{buildroot}/%{_includedir}/vc/
cp include/interface/vcos/pthreads/vcos_platform_types.h include/interface/vcos/pthreads/vcos_platform.h  %{buildroot}/%{_includedir}/interface/vcos/
#mkdir -p %{buildroot}/%{_includedir}/interface/vcos/
#mkdir -p %{buildroot}/%{_includedir}/interface/vmcs_host/
cp include/interface/vmcs_host/linux/vchost_config.h %{buildroot}/%{_includedir}/interface/vmcs_host/

echo '/%{sourcedir}/src -> /usr/share/raspberrypi-vc-demo-source'
mkdir -p              %{buildroot}/%{_datadir}/raspberrypi-vc-demo-source
cp -R -p -v src/* %{buildroot}/%{_datadir}/raspberrypi-vc-demo-source

# Previous versions of the tarball from upstream had precompiled
# libraries in /usr/share/raspberrypi-vc-demo-source/hello_pi/libs,
# which were moved to system include and library directories. The
# tarball now includes source instead.

# strip binaries and libraries. We don't have source, so skip the debug pkg.
# The exception is the static library provided in the demo source code.
strip %{buildroot}/%{_bindir}/*     || true
strip %{buildroot}/%{_sbindir}/*    || true
strip %{buildroot}/%{_libdir}/*.so* || true
strip %{buildroot}/%{_libdir}/plugins/*   || true

#exit vc dir
cd -

# Firmware in /boot
mkdir -p %{buildroot}/boot
cp -p -v boot/start* boot/fixup* boot/bootcode.bin %{buildroot}/boot
chmod a-x %{buildroot}/boot/*

#==========================

%postun
/sbin/ldconfig

%files static
%defattr(0644,root,root,0755)
#%{_libdir}/*.a
%doc boot/LICENCE.broadcom

%files libs
%defattr(0755,root,root,0755)
%{_libdir}/vc/*
%doc boot/LICENCE.broadcom

%files utils
%defattr(0755,root,root,0755)
%attr(4755,root,root)%{_bindir}/*
%attr(4755,root,root)%{_sbindir}/*
%doc boot/LICENCE.broadcom

%files libs-devel
%defattr(0644,root,root,0755)
%{_includedir}/*
%{_libdir}/pkgconfig/*
/etc/ld.so.conf.d/libs.conf
%doc boot/LICENCE.broadcom

%files demo-source
%defattr(0644,root,root,0755)
%{_datadir}/raspberrypi-vc-demo-source
%doc boot/LICENCE.broadcom

%files firmware
%defattr(-,root,root,-)
/boot/*
%doc boot/LICENCE.broadcom

%changelog
* Sat Mar 28 2015 Kevin Ross <me@kevinross.name> - 20150328git3ef516e-2.rpfr21
- Updated "%setup" to fall closer in line with packaging guidelines
- Added pkgconfig
- Updated Requires wrt pkgconfig
- Updated to latest git snapshot

* Fri Aug 08 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140808gitdf36e8d-2.rpfr20
- Added provdies for libvcsm.so to vc-libs subpackage

* Fri Aug 08 2014 pidora-auto-build - 20140808gitdf36e8d-20.rpfr20
- updated to latest commit

* Wed Jul 02 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140630git1682505-19.rpfr20
- updated to firmware/userland to latest commit

* Tue Jun 24 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140618git462f3e3-18.rpfr20
- updated userland and firmware to latest commits

* Tue Jun 17 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140616git5bb0317-17.rpfr20
- updated firmware to latest commit

* Fri Jun 13 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140611gite45a4a2-16.rpfr20
- updated userland and firmware to latest commit

* Wed May 21 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140516git97082b6-15.rpfr20
- Updated firmware and userland to latest commit also added missing commit date
  to userland

* Tue Apr 29 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140428git316b922-14.rpfr20
- updated to latest commit

* Thu Apr 10 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140117git940dc3b-13.rpfr20
- Added userland source files to build vc-demos from source

* Thu Mar 27 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140117git940dc3b-12.rpfr20
- uncommented vc header patch

* Tue Jan 28 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140117git940dc3b-8.rpfr20
- Added provides gl2.h to lib-devel

* Wed Jan 22 2014 Andrew Greene <andrew.greene@senecacollege.ca> - 20140117git940dc3b-7.rpfr20
- Initial build for pidora 2014 updated to latest commit

* Fri Nov 29 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20131128gitf7e9bcd-6.rpfr19
- updated to latest commit

* Mon Oct 28 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20131018git4c14569-5.rpfr18
- Updated to latest commit

* Thu Oct 17 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20131012git5113ce6-4.rpfr19
- Initial build for Pidora 19

* Wed Oct 16 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20131012git5113ce6-3.rpfr18
- Updated to latest commit

* Mon Sep 30 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20130918gitfadc4cb-2.rpfr18
- Added missing firmware files

* Thu Sep 19 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20130918gitfadc4cb-1.rpfr18
- Updated to latest commit

* Mon Sep 16 2013 Andrew Greene <andrew.greene@senecacollege.ca> - 20130910git7d8a762-1.rpfr18
- Updated to latest firmware

* Wed Aug 21 2013 andrew.greene@senecacollege.ca - 20130819git5b37b2a-1.rpfr18
- Updated to latest commit

* Fri Aug 16 2013 andrew.greene@senecacollege.ca - 20130815gite0590d6-1.rpfr18
- Updated to latest commit

* Mon Jul 15 2013 andrew.greene@senecacollege.ca - 20130711git245f716-3.rpfr18
- updated to latest commit moved header/lib files to subdirectory to deal with
  mesa lib conflicts and khrplatform conflicts

* Wed Jul 03 2013 andrew.greene@senecacollege.ca - 20130702gita36d33d-2.rpfr18
- moved conflicting headers to a sub dir and included a ld.so.conf.d file for
  conflicting libs

* Tue Jul 02 2013 andrew.greene@senecacollege.ca - 20130702gita36d33d-1.rpfr18
- Added provides for conflicts with mesa-libEGL-devel libs and updated firmware
  to latest commit

* Tue Jun 11 2013 andrew.greene@senecacollege.ca - 20130607git0d1b1d8-2.rpfr18
- updated to latest commit

* Wed May 15 2013 Chris Tyler <chris@tylers.info> - 20130415git1c339b1-1.rpfr18
- Updated to upstream, added suid on utils

* Fri Apr 19 2013 andrew.greene@senecacollege.ca - 20130410git7fcb9d3-2.rpfr18
- Included provides for libs libmmal_core and libmmal_util these are needed for vc-utils 

* Tue Apr 16 2013 andrew.greene@senecacollege.ca - 20130410git7fcb9d3eb2-1.rpfr18
- Updated to latest version changed vchost_config.h location

* Sat Mar 02 2013 andrew.greene@senecacollege.ca - 20121125git7e9ac50-7.rpfr18
- Copied missing header file to the correct location vchost_config.h vcos_platform_types.h and vcos_platform.h 

* Fri Mar 01 2013 andrew.greene@senecacollege.ca - 20121125git7e9ac50-4.rpfr18
- rebuilt for armv6hl

* Fri Mar 01 2013 andrew.greene@senecacollege.ca - 20121125git7e9ac50-3.rpfr18
- Added a provides tag

* Tue Nov 27 2012 Andrew Greene <andrew.greene@senecacollege.ca> - 20121125git7e9ac50-2.rpfr18
- Updated package release tag for rpfr18

* Tue Nov 27 2012 Chris Tyler <chris@tylers.info> - 20121125git7e9ac50-2.rpfr17
- Added provides for library subpackage
- Added softfp/hardfp binary selection

* Sun Nov 25 2012 Chris Tyler <chris@tylers.info> - 20121125git7e9ac50-1.rpfr17
- Updated to upstream

* Wed Sep 26 2012 Chris Tyler <chris@tylers.info> - 20120926gitb87bc42-1.rpfr17
- Updated to upstream

* Mon Aug 13 2012 Chris Tyler <chris@tylers.info> - 20120813gitcb9513f-1.rpfr17
- Updated to upstream
- Merged raspberrypi-firmware (now named raspberrypi-vc-firmware)

* Wed Aug 08 2012 Chris Tyler <chris@tylers.info> - 20120727git0d88fba-1.rpfr17
- Updated to upstream

* Wed Jul 04 2012 Chris Tyler <chris@tylers.info> - 20120703git0671d60-2.rpfr17
- Path and patch fixups

* Wed Jul 04 2012 Chris Tyler <chris@tylers.info> - 20120703git0671d60-1.rpfr17
- Updated to current upstream, adjusted for git commit in version

* Mon Mar 05 2012 Chris Tyler <chris@tylers.info> - 20120217-4
- Added path fixup for demo source code

* Mon Mar 05 2012 Chris Tyler <chris@tylers.info> - 20120217-3
- Fixed up move from vc/ subdir in /usr/include.

* Mon Mar 05 2012 Chris Tyler <chris@tylers.info> - 20120217-2
- Removed strip on libilclient.a, moved ilclient.h

* Tue Feb 21 2012 - Chris Tyler <chris.tyler@senecacollege.ca> - 20120217-1
- Initial packaging
