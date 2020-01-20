%global tarball xf86-video-qxl
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/drivers

# Xspice is x86_64 only since spice-server is x86_64 only
%ifarch x86_64
%define with_xspice (0%{?fedora} || 0%{?rhel} > 6)
%else
%define with_xspice 0
%endif

#% global gitdate 20130703
%global gitversion 8b03ec16

%if 0%{?gitdate}

%define gver .%{gitdate}git%{gitversion}
%endif

Summary:   Xorg X11 qxl video driver
Name:      xorg-x11-drv-qxl

Version:   0.1.1

Release:   18%{?gver}%{?dist}
URL:       http://www.x.org
Source0:   http://xorg.freedesktop.org/releases/individual/driver/%{tarball}-%{version}.tar.bz2

#Source0: %{tarball}-%{gitdate}.tar.bz2
Patch1:    qxl-kms-disable-composite.patch

# This should go away with a spice server containing 1d18b7e98ab268c755933061d77ccc7a981815e2
Patch2:        0005-spiceqxl_display-only-use-qxl-interface-after-it-is-.patch

Patch3: no-surfaces-kms.patch
Patch4: 0001-worst-hack-of-all-time-to-qxl-driver.patch
Patch5: disable-surfaces.patch

# Fixes for running with Xorg suid, which is the only way we ship in fedora
Patch6: 0006-spiceqxl_spice_server-no-need-to-call-spice_server_s.patch
Patch7: 0007-xspice-chown-both-files-used-by-vdagent-for-suid-Xor.patch
Patch8: 0008-Xspice-cleanup-non-regular-files-too.patch
Patch9: 0009-Xspice-fix-cleanup-when-some-processes-are-already-d.patch
Patch10: 0010-Xspice-cleanup-vdagent-files.patch
Patch11: 0011-drm-restore-cursor-after-resolution-change.patch
Patch12: 0012-Remove-call-to-CrtcRotate.patch
Patch13: 0013-drm-fail-gracefuly-on-monitor-resize.patch
Patch14: 0014-Use-pci_io_write8-instead-of-outb.patch
Patch15: 0015-Update-drm-properties-correctly.patch
Patch16: 0016-kms-initialize-primary-surface-to-screen-virtual-siz.patch
Patch17: 0017-kms-do-not-overwrite-screen-virtualX-Y.patch
Patch18: 0018-Assert-on-QXL_INTERRUPT_ERROR.patch
Patch19: 0019-Check-qxl_download_box-arguments.patch
Patch20: 0020-Dynamically-adjust-chunk-size-to-avoid-command-buffe.patch
Patch21: 0021-Don-t-leak-ARGB-cursor-data-bo.patch

License:   MIT
Group:     User Interface/X Hardware Support

ExcludeArch: s390 s390x

BuildRequires: pkgconfig
BuildRequires: xorg-x11-server-devel >= 1.1.0-1
BuildRequires: spice-protocol >= 0.12.1
BuildRequires: libdrm-devel >= 2.4.46-1

%ifarch x86_64
BuildRequires: spice-server-devel >= 0.8.0
%endif
BuildRequires: glib2-devel
BuildRequires: libtool
BuildRequires: libudev-devel

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
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1

%build
autoreconf -f -i
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
* Fri Aug 28 2015 Christophe Fergeau <cfergeau@redhat.com> 0.1.1-18
- Rebuild after tagging rebased xorg-x11-server in the build root
  Related: rhbz#1221909

* Wed Aug 26 2015 Christophe Fergeau <cfergeau@redhat.com> 0.1.1-17
- Fix freeze in xfig when entering space character
  Resolves: rhbz#1221909
- Fix memory leak
  Resolves: rhbz#1222038
- Fix cursor leak causing a crash when running RHEL6 anaconda in a VM
  Resolves: rhbz#1222040

* Fri May 22 2015 Marc-Andre Lureau <marcandre.lureau@redhat.com> - 0.1.1-16
- Fix glitches when restarting X server
  Resolves: rhbz#1102175
- Fix restarting X server
  Resolves: rhbz#1185807

* Tue May 19 2015 Jonathon Jongsma <jjongsma@redhat.com> - 0.1.1-15
- Update drm properties correctly
  Resolves: rhbz#1153377

* Fri May 15 2015 Christophe Fergeau <cfergeau@redhat.com> 0.1.1-14
- Add upstream patch fixing aarch64 build
  Resolves: rhbz#1221328

* Wed May 13 2015 Adam Jackson <ajax@redhat.com> 0.1.1-13
- Rebuild for xserver 1.17

* Thu Nov 20 2014 Marc-Andre Lureau <mlureau@redhat.com> 0.1.1-12
- Try to fallback to previous working configuration if
  drmModeSetCrtc() failed.
  Resolves: rhbz#1127552

* Thu Oct 23 2014 Christophe Fergeau <cfergeau@redhat.com> 0.1.1-11
- Fix crash when attempting to call CrtcRotate
  Resolves: rhbz#1067709

* Thu Oct 23 2014 Christophe Fergeau <cfergeau@redhat.com> 0.1.1-10
- Fix mouse cursor disappearing when changing guest resolution
  Resolves: rhbz#1030531

* Tue Mar 11 2014 Soren Sandmann <ssp@redhat.com> 0.1.1-9
- Disable surfaces by default -- bug 1070984 

* Tue Jan 14 2014 Dave Airlie <airlied@redhat.com> 0.1.1-8
- grab patches from F20 - fix dates

* Mon Jan 13 2014 Adam Jackson <ajax@redhat.com> - 0.1.1-7
- 1.15 ABI rebuild

* Tue Dec 17 2013 Adam Jackson <ajax@redhat.com> - 0.1.1-6
- 1.15RC4 ABI rebuild

* Wed Nov 20 2013 Adam Jackson <ajax@redhat.com> - 0.1.1-5
- 1.15RC2 ABI rebuild

* Wed Nov 06 2013 Adam Jackson <ajax@redhat.com> - 0.1.1-4
- 1.15RC1 ABI rebuild

* Fri Oct 25 2013 Adam Jackson <ajax@redhat.com> - 0.1.1-3
- ABI rebuild

* Thu Oct 24 2013 Adam Jackson <ajax@redhat.com> 0.1.1-2
- Drop qxl rev 1 patches

* Mon Oct 21 2013 Alon Levy <alevy@redhat.com> - 0.1.1-1
- New upstream release
- Fixes to said release to work with suid issues (upstream)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.1-0.14.20130514git77a1594
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 03 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.13
- resnapshot upstream to pick up a few patches
- add userspace patch to use new kernel hotspot interface (#974662)

* Wed Jul 03 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.12
- add support for udev event catching - for dynamic resize from kernel

* Tue Jul 02 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.11
- helps if you apply the patch (#978612)

* Sat Jun 29 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.10
- fix another resize issue due (#978612)

* Tue Jun 18 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.9
- disable composite/a8 surfaces for KMS (#974198)

* Tue May 28 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.8
- fix 32-bit (#965101)

* Tue May 14 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.7
- resnapshot - fixes randr under KMS

* Tue May 14 2013 Daniel Mach <dmach@redhat.com> - 0.1.1-0.6
- Fix with_xspice macro definition (airlied - cherrypick)

* Tue May 7 2013 Alon Levy <alevy@redhat.com> 0.1.1-0.5
- Add Xspice fixes and dfps (upstream a474a71..77a1594)

* Tue Mar 19 2013 Adam Jackson <ajax@redhat.com> 0.1.1-0.4
- Less RHEL customization

* Tue Mar 12 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.3.20130312gita474a71
- add KMS support to userspace driver

* Thu Mar 07 2013 Peter Hutterer <peter.hutterer@redhat.com> - 0.1.1-0.2.20130306git9d45cc5
- ABI rebuild

* Wed Mar 06 2013 Dave Airlie <airlied@redhat.com> 0.1.1-0.1
- bump to get UMS bo abstraction in - kms coming soon

* Fri Feb 15 2013 Peter Hutterer <peter.hutterer@redhat.com> - 0.1.0-4
- ABI rebuild

* Fri Feb 15 2013 Peter Hutterer <peter.hutterer@redhat.com> - 0.1.0-3
- ABI rebuild

* Thu Jan 10 2013 Adam Jackson <ajax@redhat.com> - 0.1.0-2
- ABI rebuild

* Sat Sep 22 2012 Soren Sandmann <ssp@redhat.com> 0.1.0-1
- Upstream 0.1.0

* Wed Aug 29 2012 Adam Jackson <ajax@redhat.com> 0.0.22-6
- Exclude Xspice from RHEL6 builds

* Sun Aug 26 2012 Alon Levy <alevy@redhat.com>
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

* Fri Oct 28 2011 Soren Sandmann <ssp@redhat.com> - 0.0.21-8
- Bump release

* Fri Oct 28 2011 Soren Sandmann <ssp@redhat.com> - 0.0.21-7
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
