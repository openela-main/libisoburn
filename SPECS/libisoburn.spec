%global pkgname libisoburn

Summary:         Library to enable creation and expansion of ISO-9660 filesystems
Name:            libisoburn
Version:         1.5.4
Release:         4%{?dist}
License:         GPLv2+
URL:             https://libburnia-project.org/
Source0:         https://files.libburnia-project.org/releases/%{pkgname}-%{version}.tar.gz
Source1:         https://files.libburnia-project.org/releases/%{pkgname}-%{version}.tar.gz.sig
Source2:         gpgkey-44BC9FD0D688EB007C4DD029E9CBDFC0ABC0A854.gpg
Source3:         xorriso_extract_iso_image.desktop
Patch0:          libisoburn-1.0.8-multilib.patch
BuildRequires:   gnupg2
BuildRequires:   gcc, gcc-c++, make, readline-devel, libacl-devel, zlib-devel
BuildRequires:   chrpath
%if 0%{?rhel} == 7
BuildRequires:   autoconf, automake, libtool
BuildRequires:   libburn1-devel >= %{version}, libisofs1-devel >= %{version}
%else
%if (0%{?rhel} && "%{name}" != "%{pkgname}")
BuildRequires:   autoconf, automake, libtool
%global variant 1
%endif
BuildRequires:   libburn%{?variant}-devel >= %{version}
BuildRequires:   libisofs%{?variant}-devel >= %{version}
%endif

%description
Libisoburn is a front-end for libraries libburn and libisofs which
enables creation and expansion of ISO-9660 filesystems on all CD/
DVD/BD media supported by libburn. This includes media like DVD+RW,
which do not support multi-session management on media level and
even plain disk files or block devices. Price for that is thorough
specialization on data files in ISO-9660 filesystem images. And so
libisoburn is not suitable for audio (CD-DA) or any other CD layout
which does not entirely consist of ISO-9660 sessions.

%package devel
Summary:         Development files for %{name}
Requires:        %{name}%{?_isa} = %{version}-%{release}, pkgconfig

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%if 0%{!?_without_doc:1}
%package doc
Summary:         Documentation files for %{name}
BuildArch:       noarch
BuildRequires:   doxygen, graphviz

%description doc
Libisoburn is a front-end for libraries libburn and libisofs which
enables creation and expansion of ISO-9660 filesystems on all CD/
DVD/BD media supported by libburn. And this package contains the API
documentation for developing applications that use %{name}.
%endif

%package -n xorriso%{?variant}
Summary:         ISO-9660 and Rock Ridge image manipulation tool
URL:             http://scdbackup.sourceforge.net/xorriso_eng.html
Requires:        %{name}%{?_isa} = %{version}-%{release}
%if 0%{!?_without_kde:1} && (0%{?fedora} || 0%{?rhel} == 7 || (0%{?rhel} && "%{name}" != "%{pkgname}"))
Requires:        kde-filesystem >= 4
Requires:        kf5-filesystem >= 5
%endif
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires(post):  /sbin/install-info
Requires(preun): /sbin/install-info
%endif
Requires(post):  %{_sbindir}/alternatives, coreutils
Requires(preun): %{_sbindir}/alternatives
Provides: cdrecord
Provides: wodim
Provides: mkisofs
Provides: genisoimage

%description -n xorriso%{?variant}
Xorriso is a program which copies file objects from POSIX compliant
filesystems into Rock Ridge enhanced ISO-9660 filesystems and allows
session-wise manipulation of such filesystems. It can load management
information of existing ISO images and it writes the session results
to optical media or to filesystem objects. Vice versa xorriso is able
to copy file objects out of ISO-9660 filesystems.

Filesystem manipulation capabilities surpass those of mkisofs. Xorriso
is especially suitable for backups, because of its high fidelity of
file attribute recording and its incremental update sessions. Optical
supported media: CD-R, CD-RW, DVD-R, DVD-RW, DVD+R, DVD+R DL, DVD+RW,
DVD-RAM, BD-R and BD-RE.

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%setup -q -n %{pkgname}-%{version}
%patch0 -p1 -b .multilib

# Use libisofs1 and libburn1 on EPEL
%if 0%{?rhel} == 7 || (0%{?rhel} && "%{name}" != "%{pkgname}")
sed -e 's@\(libisofs\|libburn\)-1.pc@\11-1.pc@g' -i configure.ac
sed -e 's@\(libisofs\|libburn\)/@\11/@g' -i configure.ac */*.[hc] */*/*.cpp
sed -e 's@\(lisofs\|lburn\)@\11@g' -i Makefile.am
touch NEWS; autoreconf --force --install

# Rename from libisoburn to libisoburn1 for EPEL >= 8
%if 0%{?rhel} >= 8
sed -e 's@libisoburn_libisoburn@libisoburn_libisoburn1@g' \
    -e 's@libisoburn/libisoburn.la@libisoburn/libisoburn1.la@g' \
    -e 's@(includedir)/libisoburn@(includedir)/libisoburn1@g' \
    -e 's@libisoburn-1.pc@libisoburn1-1.pc@g' \
    -e 's@ln -s xorriso@ln -s xorriso%{?variant}@g' -i Makefile.am
sed -e 's@libisoburn-1.pc@libisoburn1-1.pc@g' -i configure.ac
sed -e 's@isoburn@isoburn1@g' libisoburn-1.pc.in > libisoburn1-1.pc.in

libtoolize --force
autoreconf --force --install
%endif
%endif

%build
%configure --disable-static
%make_build
%{!?_without_doc:doxygen doc/doxygen.conf}

%install
%make_install

# Don't install any libtool .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}.la

# Clean up for later usage in documentation
rm -rf $RPM_BUILD_ROOT%{_defaultdocdir}

# Install the KDE service menu handler
%if 0%{!?_without_kde:1} && (0%{?fedora} || 0%{?rhel} == 7 || (0%{?rhel} && "%{name}" != "%{pkgname}"))
install -D -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/kde4/services/ServiceMenus/xorriso_extract_iso_image.desktop
install -D -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/kservices5/ServiceMenus/xorriso_extract_iso_image.desktop
%endif

# Remove runpath
chrpath -d $RPM_BUILD_ROOT%{_bindir}/xorriso

# RHEL ships a xorriso package already
%if 0%{?rhel} && "%{name}" != "%{pkgname}"
mv -f $RPM_BUILD_ROOT%{_bindir}/osirrox{,%{?variant}}
mv -f $RPM_BUILD_ROOT%{_bindir}/xorrecord{,%{?variant}}
mv -f $RPM_BUILD_ROOT%{_bindir}/xorriso{,%{?variant}}
mv -f $RPM_BUILD_ROOT%{_bindir}/xorrisofs{,%{?variant}}
mv -f $RPM_BUILD_ROOT%{_bindir}/xorriso-dd-target{,%{?variant}}
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/xorrecord{,%{?variant}}.1
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/xorriso{,%{?variant}}.1
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/xorrisofs{,%{?variant}}.1
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/xorriso-dd-target{,%{?variant}}.1
mv -f $RPM_BUILD_ROOT%{_infodir}/xorrecord{,%{?variant}}.info
mv -f $RPM_BUILD_ROOT%{_infodir}/xorriso{,%{?variant}}.info
mv -f $RPM_BUILD_ROOT%{_infodir}/xorrisofs{,%{?variant}}.info
mv -f $RPM_BUILD_ROOT%{_infodir}/xorriso-dd-target{,%{?variant}}.info
%if 0%{!?_without_kde:1}
sed -e 's@ xorriso @ xorriso%{?variant} @g' \
  -i $RPM_BUILD_ROOT%{_datadir}/{kde4/services,kservices5}/ServiceMenus/xorriso_extract_iso_image.desktop
touch -c -r %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/{kde4/services,kservices5}/ServiceMenus/xorriso_extract_iso_image.desktop
%endif
%endif

# Prepare alternatives handling for cdrecord, wodim -> xorrecord and mkisofs, genisoimage -> xorriso
touch $RPM_BUILD_ROOT{%{_bindir}/{cdrecord,wodim,mkisofs,genisoimage},%{_mandir}/man1/{cdrecord,wodim,mkisofs,genisoimage}.1.gz}

# Some file cleanups
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

# Don't ship proof of concept for the moment
rm -f $RPM_BUILD_ROOT{%{_bindir},%{_infodir},%{_mandir}/man1}/xorriso-tcltk*

%check
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$RPM_BUILD_ROOT%{_libdir}"
cd releng
./run_all_auto -x ../xorriso/xorriso || (cat releng_generated_data/log.*; exit 1)

%ldconfig_scriptlets

%post -n xorriso%{?variant}
%if 0%{?rhel} == 7
/sbin/install-info %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :
%endif

%{_sbindir}/alternatives --install %{_bindir}/cdrecord cdrecord %{_bindir}/xorrecord%{?variant} 50 \
  --slave %{_mandir}/man1/cdrecord.1.gz cdrecord-cdrecordman %{_mandir}/man1/xorrecord%{?variant}.1.gz \
  --slave %{_bindir}/wodim cdrecord-wodim %{_bindir}/xorrecord%{?variant} \
  --slave %{_mandir}/man1/wodim.1.gz cdrecord-wodimman %{_mandir}/man1/xorrecord%{?variant}.1.gz
%{_sbindir}/alternatives --install %{_bindir}/mkisofs mkisofs %{_bindir}/xorrisofs%{?variant} 50 \
  --slave %{_mandir}/man1/mkisofs.1.gz mkisofs-mkisofsman %{_mandir}/man1/xorrisofs%{?variant}.1.gz \
  --slave %{_bindir}/genisoimage mkisofs-genisoimage %{_bindir}/xorrisofs%{?variant} \
  --slave %{_mandir}/man1/genisoimage.1.gz mkisofs-genisoimageman %{_mandir}/man1/xorrisofs%{?variant}.1.gz

%preun -n xorriso%{?variant}
if [ $1 -eq 0 ]; then
%if 0%{?rhel} == 7
  /sbin/install-info --delete %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorriso-dd-target.info.gz %{_infodir}/dir || :
%endif

  %{_sbindir}/alternatives --remove cdrecord %{_bindir}/xorrecord%{?variant}
  %{_sbindir}/alternatives --remove mkisofs %{_bindir}/xorrisofs%{?variant}
fi

%files
%license COPYING
%doc AUTHORS COPYRIGHT README ChangeLog
%{_libdir}/%{name}*.so.*

%files devel
%{_includedir}/%{name}
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}*.pc

%if 0%{!?_without_doc:1}
%files doc
%doc doc/html/
%endif

%files -n xorriso%{?variant}
%ghost %{_bindir}/cdrecord
%ghost %{_bindir}/wodim
%ghost %{_bindir}/mkisofs
%ghost %{_bindir}/genisoimage
%{_bindir}/osirrox%{?variant}
%{_bindir}/xorrecord%{?variant}
%{_bindir}/xorriso%{?variant}
%{_bindir}/xorrisofs%{?variant}
%{_bindir}/xorriso-dd-target%{?variant}
%ghost %{_mandir}/man1/cdrecord.1*
%ghost %{_mandir}/man1/wodim.1*
%ghost %{_mandir}/man1/mkisofs.1*
%ghost %{_mandir}/man1/genisoimage.1*
%{_mandir}/man1/xorrecord%{?variant}.1*
%{_mandir}/man1/xorriso%{?variant}.1*
%{_mandir}/man1/xorrisofs%{?variant}.1*
%{_mandir}/man1/xorriso-dd-target%{?variant}.1*
%{_infodir}/xorrecord%{?variant}.info*
%{_infodir}/xorriso%{?variant}.info*
%{_infodir}/xorrisofs%{?variant}.info*
%{_infodir}/xorriso-dd-target%{?variant}.info*
%if 0%{!?_without_kde:1} && (0%{?fedora} || 0%{?rhel} == 7 || (0%{?rhel} && "%{name}" != "%{pkgname}"))
%{_datadir}/kde4/services/ServiceMenus/xorriso_extract_iso_image.desktop
%{_datadir}/kservices5/ServiceMenus/xorriso_extract_iso_image.desktop
%endif

%changelog
* Tue Feb 08 2022 Jiri Kucera <jkucera@redhat.com> - 1.5.4-4
- Provide alternatives
  Resolves: #1967484

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.5.4-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.5.4-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Mon Feb 08 2021 Robert Scheck <robert@fedoraproject.org> 1.5.4-1
- Upgrade to 1.5.4 (#1926005)

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Dec 28 2020 Robert Scheck <robert@fedoraproject.org> 1.5.2-5
- Don't ship API docs twice (devel and doc subpackages)
- Reworked spec file to build libisoburn1 for RHEL >= 8

* Mon Sep 28 2020 Troy Dawson <tdawson@redhat.com> - 1.5.2-4
- No kde or kf5 filesystem for RHEL 8 or above.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Oct 27 2019 Robert Scheck <robert@fedoraproject.org> 1.5.2-1
- Upgrade to 1.5.2 (#1765954)

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Feb 17 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.5.0-3
- Rebuild for readline 8.0

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Dec 08 2018 Robert Scheck <robert@fedoraproject.org> 1.5.0-1
- Upgrade to 1.5.0
- Provide KDE service menu entry for KDE 4 and 5 (#1633872)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Sep 15 2017 Robert Scheck <robert@fedoraproject.org> 1.4.8-1
- Upgrade to 1.4.8 (#1491482)

* Thu Aug 24 2017 Robert Scheck <robert@fedoraproject.org> 1.4.6-7
- Move large documentation into -doc subpackage

* Sun Aug 13 2017 Robert Scheck <robert@fedoraproject.org> 1.4.6-6
- Added upstream patch to avoid %%check failure due to tput error

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.4.6-2
- Rebuild for readline 7.x

* Sun Sep 18 2016 Robert Scheck <robert@fedoraproject.org> 1.4.6-1
- Upgrade to 1.4.6 (#1377002)

* Tue Jul 05 2016 Robert Scheck <robert@fedoraproject.org> 1.4.4-1
- Upgrade to 1.4.4 (#1352345)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Dec 24 2015 Robert Scheck <robert@fedoraproject.org> 1.4.2-1
- Upgrade to 1.4.2 (#1287353)
- Add symlink handling via alternatives for mkisofs (#1256240)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Robert Scheck <robert@fedoraproject.org> 1.4.0-1
- Upgrade to 1.4.0 (#1222525)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 29 2014 Robert Scheck <robert@fedoraproject.org> 1.3.8-1
- Upgrade to 1.3.8 (#1078719)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Mar 05 2014 Robert Scheck <robert@fedoraproject.org> 1.3.6-1
- Upgrade to 1.3.6 (#1072838)

* Sat Dec 14 2013 Robert Scheck <robert@fedoraproject.org> 1.3.4-1
- Upgrade to 1.3.4 (#1043070)

* Sun Aug 25 2013 Robert Scheck <robert@fedoraproject.org> 1.3.2-1
- Upgrade to 1.3.2 (#994920)

* Sat Aug 03 2013 Robert Scheck <robert@fedoraproject.org> 1.3.0-1
- Upgrade to 1.3.0 (#965233)
- Run autoreconf to recognize aarch64

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Mar 19 2013 Robert Scheck <robert@fedoraproject.org> 1.2.8-1
- Upgrade to 1.2.8

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jan 12 2013 Robert Scheck <robert@fedoraproject.org> 1.2.6-1
- Upgrade to 1.2.6 (#893693)

* Sat Aug 11 2012 Robert Scheck <robert@fedoraproject.org> 1.2.4-1
- Upgrade to 1.2.4 (#842078)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun May 13 2012 Robert Scheck <robert@fedoraproject.org> 1.2.2-1
- Upgrade to 1.2.2

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Nov 27 2011 Robert Scheck <robert@fedoraproject.org> 1.1.8-1
- Upgrade to 1.1.8

* Sun Oct 09 2011 Robert Scheck <robert@fedoraproject.org> 1.1.6-1
- Upgrade to 1.1.6

* Sun Jul 10 2011 Robert Scheck <robert@fedoraproject.org> 1.1.2-1
- Upgrade to 1.1.2

* Mon May 02 2011 Robert Scheck <robert@fedoraproject.org> 1.0.8-2
- Added forgotten documentation files to %%files (#697326 #c1)

* Sun Apr 17 2011 Robert Scheck <robert@fedoraproject.org> 1.0.8-1
- Upgrade to 1.0.8
- Initial spec file for Fedora and Red Hat Enterprise Linux
