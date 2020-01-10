%global tarball xf86-video-qxl
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/drivers

# Xspice is x86_64 only since spice-server is x86_64 only
%ifarch x86_64
%define with_xspice 0%{?fedora} || 0%{?rhel} > 6
%else
%define with_xspice 0
%endif

%if 0%{?gitdate}
%define gver .%{gitdate}git%{gitversion}
%endif

Summary:   Xorg X11 qxl video driver
Name:      xorg-x11-drv-qxl

# This is hack since a driver got built with the version number 0.0.20.f14b
Version:   0.1.0

Release:   7%{?gver}%{?dist}
URL:       http://www.x.org
Source0:   http://xorg.freedesktop.org/releases/individual/driver/%{tarball}-%{version}.tar.bz2
#Source0: %{tarball}-%{gitdate}.tar.bz2
# Support for old revision 1 qxl device (which won't go upstream)

Patch1:    0001-Add-old-driver-in-as-a-compatibility-layer.patch
Patch2:    0002-Link-in-the-compat-driver-various-renamings.patch
Patch3:    0003-compat-bump-to-new-server-API-changes.patch
Patch4:	   0001-Add-new-DebugRenderFallbacks-option.patch
Patch5:	   0002-When-DebugRenderFallbacks-is-turned-on-print-debug-s.patch
Patch6:    disable-surfaces.patch

Patch7:     0007-qxl_driver-remove-unused-enum-ROPDescriptor.patch
Patch8:     0008-qxl_pre_init-fix-calculation-of-available-video-memo.patch
Patch9:     0009-qxl_driver-check_crtc-handle-qxl-crtcs-NULL.patch
Patch10:    0010-qxl_driver-simplify-calling-qxl_update_monitors_conf.patch
Patch11:    0011-qxl_driver-monitors_config-adjust-to-memory-remap.patch
Patch12:    0001-compat-driver-Make-sure-to-initialize-the-VGA-functi.patch

Patch13:    0013-Establish-a-preferred-default-of-1024x768-correctly.patch
Patch14:    0014-More-correctly-signal-that-we-only-want-the-first-he.patch

License:   MIT
Group:     User Interface/X Hardware Support

ExcludeArch: s390 s390x %{?rhel:ppc ppc64}

BuildRequires: pkgconfig
BuildRequires: xorg-x11-server-devel >= 1.13.0-1
BuildRequires: spice-protocol >= 0.12.0
%ifarch x86_64
BuildRequires: spice-server-devel >= 0.8.0
%endif
BuildRequires: glib2-devel
BuildRequires: libtool

Requires: Xorg %(xserver-sdk-abi-requires ansic)
Requires: Xorg %(xserver-sdk-abi-requires videodrv)

%description 
X.Org X11 qxl video driver.

%if %{with_xspice}
%package -n    xorg-x11-server-Xspice
Summary:       XSpice is an X server that can be accessed by a Spice client
Requires:      Xorg %(xserver-sdk-abi-requires ansic)
Requires:      Xorg %(xserver-sdk-abi-requires videodrv)
Requires:      xorg-x11-server-Xorg
Requires:      python >= 2.6

%description -n xorg-x11-server-Xspice
XSpice is both an X and a Spice server.
%endif

%prep
%setup -q -n %{tarball}-%{?gitdate:%{gitdate}}%{!?gitdate:%{version}}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

autoreconf -f -i

%build
%if %{with_xspice}
%define enable_xspice --enable-xspice
%endif
%configure --disable-static %{?enable_xspice}
make %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -regex ".*\.la$" | xargs rm -f --

%ifarch x86_64
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11
install -p -m 644 examples/spiceqxl.xorg.conf.example \
    $RPM_BUILD_ROOT%{_sysconfdir}/X11/spiceqxl.xorg.conf
# FIXME: upstream installs this file by default, we install it elsewhere.
# upstream should just not install it and let dist package deal with
# doc/examples.
rm -f $RPM_BUILD_ROOT/usr/share/doc/xf86-video-qxl/spiceqxl.xorg.conf.example
%if !%{with_xspice}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/X11/spiceqxl.xorg.conf
%endif
%endif


%files
%defattr(-,root,root,-)
%doc COPYING README
%{driverdir}/qxl_drv.so

%if %{with_xspice}
%files -n xorg-x11-server-Xspice
%defattr(-,root,root,-)
%doc COPYING README.xspice README examples/spiceqxl.xorg.conf.example
%config(noreplace) %{_sysconfdir}/X11/spiceqxl.xorg.conf
%{_bindir}/Xspice
%{driverdir}/spiceqxl_drv.so
%endif


%changelog
* Fri Aug 2 2013 Alon Levy <alevy@redhat.com> 0.1.0-7
- bump release since previous build got deleted.
  Resolves: #951000

* Fri Aug 2 2013 Alon Levy <alevy@redhat.com> 0.1.0-6
- Fix hard coded 1024x768 default mode, breaking xorg.conf directives
  Resolves: #951000

* Fri Aug 2 2013 Soren Sandmann <ssp@redhat.com> 0.1.0-5
- compat driver: Initialize VGA functions
  Related: #929037

* Sun Jan 20 2013 Uri Lublin <uril@redhat.com> 0.1.0-4
- Adjust monitors_config to memory remap
  Resolves: #883578

* Wed Jan 16 2013 Soren Sandmann <ssp@redhat.com> 0.1.0-3
- Add patches to add DebugRenderFallbacks option
- Add patch to disable surfaces

* Fri Sep 28 2012 Adam Jackson <ajax@redhat.com> 0.1.0-2
- Fix xserver BuildRequires for 6.4

* Tue Sep 25 2012 Soren Sandmann <ssp@redhat.com> 0.1.0-1
- Update to upstream version 0.1.0; bz #835249

* Wed Aug 29 2012 Adam Jackson <ajax@redhat.com> 0.0.22-6
- Exclude Xspice from RHEL6 builds

* Thu Aug 26 2012 Alon Levy <alevy@redhat.com>
- fix uxa_xorg_enable_disable_fb_access - 0.0.22-5.20120718gitde6620788 (#844463)

* Thu Aug 23 2012 Alon Levy <alevy@redhat.com>
- fix break from introduction of screen privates - 0.0.22-4.20120718gitde6620788 (#844463)

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.22-3.20120718gitde6620788
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 18 2012 Dave Airlie <airlied@redhat.com> 0.0.22-2.20120718gitde6620788
- git snapshot for new server API

* Thu Apr 05 2012 Adam Jackson <ajax@redhat.com> - 0.0.22-1
- RHEL arch exclude updates

* Thu Mar 15 2012 Soren Sandmann <ssp@redhat.com> - 0.22.0
- Upstream 0.0.17

* Sat Feb 11 2012 Peter Hutterer <peter.hutterer@redhat.com> - 0.0.21-16
- ABI rebuild

* Fri Feb 10 2012 Peter Hutterer <peter.hutterer@redhat.com> - 0.0.21-15
- ABI rebuild

* Tue Jan 24 2012 Peter Hutterer <peter.hutterer@redhat.com> - 0.0.21-14
- ABI rebuild

* Fri Jan 13 2012 Marc-André Lureau <mlureau@redhat.com> 0.0.21-13
- Add 0011-support-_ASYNC-io-calls-and-interrupt-handling-busy-.patch
  to use async calls

* Wed Jan 04 2012 Adam Jackson <ajax@redhat.com> 0.0.21-12
- qxl-0.0.16-ftbfs.patch: Fix some FTBFS.

* Wed Nov 16 2011 Adam Jackson <ajax@redhat.com> 0.0.21-11
- qxl-0.0.16-vgahw.patch: API compat for xserver 1.12 (#753928)

* Mon Nov 14 2011 Adam Jackson <ajax@redhat.com> - 0.0.21-10
- ABI rebuild

* Wed Nov 09 2011 Adam Jackson <ajax@redhat.com> - 0.0.21-9
- ABI rebuild

* Wed Oct 28 2011 Soren Sandmann <ssp@redhat.com> - 0.0.21-8
- Bump release

* Wed Oct 28 2011 Soren Sandmann <ssp@redhat.com> - 0.0.21-7
- Add patch to translate access regions according to drawable offset
  Bug 731245.

* Thu Oct 27 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.21-7
- Rebuilt for glibc bug#747377

* Wed Oct 26 2011 Soren Sandmann <ssp@redhat.com> - 0.0.21-6
- Add patch to confine access regions to the bounds of the drawable.
  Bug 731245.

* Mon Sep 12 2011 Hans de Goede <hdegoede@redhat.com> - 0.0.21-5
- Rebase to latest upstream release
- Enable building of the Xspice X-server and put it in its own
  xorg-x11-server-Xspice package

* Thu Aug 18 2011 Adam Jackson <ajax@redhat.com> - 0.0.21-4
- Rebuild for xserver 1.11 ABI

* Wed Apr 20 2011 Hans de Goede <hdegoede@redhat.com> 0.0.21-3
- Add various bugfixes from upstream git
- Fixes VT-switching (rhbz#696711)
- Add support for old qxl device (from rhel6 branch) (rhbz#642153)

* Mon Mar 07 2011 Dave Airlie <airlied@redhat.com> 0.0.21-2
- Bump to for abi rebuild

* Sat Feb 12 2011 Soren Sandmann <ssp@redhat.com> 0.0.21-1
- New version number to make sure upgrading works

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 26 2011 Soren Sandmann <ssp@redhat.com> 0.0.13-1
- Update to 0.0.13 with surfaces

* Mon Dec 06 2010 Adam Jackson <ajax@redhat.com> 0.0.20.f14b-10
- Rebuild for new server ABI.

* Wed Oct 27 2010 Adam Jackson <ajax@redhat.com> 0.0.20.f14b-8
- Add ABI requires magic (#542742)

* Sun Oct 17 2010 Hans de Goede <hdegoede@redhat.com> 0.0.20.f14b-7
- Fix notification bubbles under gnome not showing (backport from the
  surface-fixes branch)

* Sun Oct 17 2010 Hans de Goede <hdegoede@redhat.com> 0.0.20.f14b-6
- Fix a pointer casting bug which causes the qxl driver to trigger an
  assertion in the qxl device terminating the entire virtual machine

* Mon Oct 11 2010 Hans de Goede <hdegoede@redhat.com> 0.0.20.f14b-5
- Don't access the qxl device when our vt is not focussed, this fixes
  Xorg crashing when switching to a text vc

* Sun Oct 10 2010 Hans de Goede <hdegoede@redhat.com> 0.0.20.f14b-4
- Fix the driver not working on qxl devices with a framebuffer of 8MB

* Sat Oct  9 2010 Hans de Goede <hdegoede@redhat.com> 0.0.20.f14b-3
- Add support for using resolutions > 1024x768 without needing an xorg.conf
- Restore textmode font when switching back to a textmode virtual console

* Fri Oct 08 2010 Jesse Keating <jkeating@redhat.com> - 0.0.20.f14b-2.1
- Rebuild for gcc bug 634757

* Tue Sep 14 2010 Soren Sandmann <ssp@redhat.com> 0.0.20.f14b-2
- Patch to fix it up for the new privates ABI (I had apparently been
  testing with a too old X server).

* Tue Sep 14 2010 Soren Sandmann <ssp@redhat.com> 0.0.20.f14b-1
- Add support for new device

* Sat Mar 13 2010 Dave Airlie <airlied@redhat.com> 0.0.12-2
- fix bug in qxl with asserts

* Sat Mar 13 2010 Dave Airlie <airlied@redhat.com> 0.0.12-1
- rebase to 0.0.12 release - fix some 16-bit bugs

* Mon Jan 11 2010 Dave Airlie <airlied@redhat.com> 0.0.9-0.1
- Initial public release 0.0.9
