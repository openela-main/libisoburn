Summary:         Library to enable creation and expansion of ISO-9660 filesystems
Name:            libisoburn
Version:         1.4.8
Release:         4%{?dist}
License:         GPLv2+
Group:           System Environment/Libraries
URL:             http://libburnia-project.org/
Source0:         http://files.libburnia-project.org/releases/%{name}-%{version}.tar.gz
Source1:         http://files.libburnia-project.org/releases/%{name}-%{version}.tar.gz.sig
Patch0:          libisoburn-1.0.8-multilib.patch
BuildRequires:   gcc, gcc-c++
BuildRequires:   readline-devel, libacl-devel, zlib-devel
%if 0%{?rhel} >= 6 && 0%{?rhel} <= 7
BuildRequires:   libburn1-devel >= %{version}, libisofs1-devel >= %{version}
BuildRequires:   autoconf, automake, libtool
%else
BuildRequires:   libburn-devel >= %{version}, libisofs-devel >= %{version}
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
Summary:         Development files for libisoburn
Group:           Development/Libraries
Requires:        %{name}%{?_isa} = %{version}-%{release}, pkgconfig

%description devel
The libisoburn-devel package contains libraries and header files for
developing applications that use libisoburn.

%package doc
Summary:         Documentation files for libisoburn
Group:           Documentation
%if 0%{?fedora} || 0%{?rhel} >= 6
BuildArch:       noarch
%endif
BuildRequires:   doxygen, graphviz

%description doc
Libisoburn is a front-end for libraries libburn and libisofs which
enables creation and expansion of ISO-9660 filesystems on all CD/
DVD/BD media supported by libburn. And this package contains the API
documentation for developing applications that use libisoburn.

%package -n xorriso
Summary:         ISO-9660 and Rock Ridge image manipulation tool
Group:           Applications/Archiving
URL:             http://scdbackup.sourceforge.net/xorriso_eng.html
Requires:        %{name}%{?_isa} = %{version}-%{release}
%if 0%{?rhel} >= 6 || 0%{?fedora}
Requires(post):  %{_sbindir}/alternatives, coreutils
Requires(preun): %{_sbindir}/alternatives
Provides:        mkisofs
%endif
Requires(post):  /sbin/install-info
Requires(preun): /sbin/install-info

%description -n xorriso
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
%setup -q
%patch0 -p1 -b .multilib

# Use libisofs1 and libburn1 on RHEL >= 6
%if 0%{?rhel} >= 6 && 0%{?rhel} <= 7
sed -e 's@\(libisofs\|libburn\)-1.pc@\11-1.pc@g' -i configure.ac
sed -e 's@\(libisofs\|libburn\)/@\11/@g' -i configure.ac */*.[hc] */*/*.cpp
sed -e 's@\(lisofs\|lburn\)@\11@g' -i Makefile.am
touch NEWS; autoreconf --force --install
%endif

%build
%configure --disable-static
make %{?_smp_mflags}
doxygen doc/doxygen.conf

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p' install

# Don't install any libtool .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}.la

# Clean up for later usage in documentation
rm -rf $RPM_BUILD_ROOT%{_defaultdocdir}

# Symlink xorriso as mkisofs (like in cdrkit)
%if 0%{?rhel} >= 6 || 0%{?fedora}
ln -sf xorriso $RPM_BUILD_ROOT%{_bindir}/mkisofs
%endif

# Some file cleanups
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

# Don't ship proof of concept for the moment
rm -f $RPM_BUILD_ROOT%{_bindir}/xorriso-tcltk

%check
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$RPM_BUILD_ROOT%{_libdir}"
cd releng
./run_all_auto -x ../xorriso/xorriso || (cat releng_generated_data/log.*; exit 1)

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post -n xorriso
/sbin/install-info %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :

%if 0%{?rhel} >= 6 || 0%{?fedora}
link=`readlink %{_bindir}/mkisofs`
if [ "$link" == "xorriso" ]; then
  rm -f %{_bindir}/mkisofs
fi

%{_sbindir}/alternatives --install %{_bindir}/mkisofs mkisofs %{_bindir}/xorriso 60 \
  --slave %{_mandir}/man1/mkisofs.1.gz mkisofs-mkisofsman %{_mandir}/man1/xorrisofs.1.gz
%endif

%preun -n xorriso
if [ $1 = 0 ]; then
  /sbin/install-info --delete %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :

%if 0%{?rhel} >= 6 || 0%{?fedora}
  %{_sbindir}/alternatives --remove mkisofs %{_bindir}/xorriso
%endif
fi

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS COPYRIGHT README ChangeLog
%{_libdir}/%{name}*.so.*

%files devel
%doc doc/html
%{_includedir}/%{name}
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}*.pc

%files doc
%doc doc/html/

%files -n xorriso
%if 0%{?rhel} >= 6 || 0%{?fedora}
%ghost %{_bindir}/mkisofs
%endif
%{_bindir}/osirrox
%{_bindir}/xorrecord
%{_bindir}/xorriso
%{_bindir}/xorrisofs
%{_mandir}/man1/xorrecord.1*
%{_mandir}/man1/xorriso.1*
%{_mandir}/man1/xorrisofs.1*
%{_infodir}/xorrecord.info*
%{_infodir}/xorriso.info*
%{_infodir}/xorrisofs.info*

%changelog
* Mon Jan  7 2019 Pavel Cahyna <pcahyna@redhat.com> - 1.4.8-4
- Remove KDE bits
- Provide: mkisofs (as genisoimage does)
- Increase alternative priority to win over genisoimage
- Update RHEL conditionals for lib{isofs,burn} renaming to match those packages

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
