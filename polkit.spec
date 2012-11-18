Summary:	A framework for defining policy for system-wide components
Name:		polkit
Version:	0.108
Release:	2
License:	MIT
Group:		Libraries
Source0:	http://www.freedesktop.org/software/polkit/releases/%{name}-%{version}.tar.gz
# Source0-md5:	55cd17b20030d895a7ecf1b9c9b32fb6
Source1:	%{name}.pamd
URL:		http://people.freedesktop.org/~david/polkit-spec.html
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	dbus-glib-devel
BuildRequires:	expat-devel
BuildRequires:	gobject-introspection-devel
BuildRequires:	js-devel
BuildRequires:	libtool
BuildRequires:	pam-devel
BuildRequires:	pkg-config
BuildRequires:	systemd-devel
Requires:	%{name}-libs = %{version}-%{release}
Requires:	systemd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_prefix}/lib/%{name}-1

%description
PolicyKit is a framework for defining policy for system-wide
components and for desktop pieces to configure it. It is used by HAL.

%package libs
Summary:	PolicyKit libraries
Group:		Libraries

%description libs
PolicyKit libraries.

%package devel
Summary:	Header files for PolicyKit
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for PolicyKit.

%package apidocs
Summary:	PolicyKit API documentation
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
PolicyKit API documentation.

%prep
%setup -q

# https://bugs.freedesktop.org/show_bug.cgi?id=57146
%{__sed} -i "s|libmozjs185.so|libmozjs185.so.1|" \
	src/polkitbackend/polkitbackendjsauthority.c

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules		\
	--disable-static		\
	--enable-examples=no		\
	--enable-systemd		\
	--with-html-dir=%{_gtkdocdir}	\
	--with-os-type=none
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/polkit-1/actions

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/polkit-1/extensions/*.la

install %{SOURCE1} $RPM_BUILD_ROOT/etc/pam.d/polkit-1

%find_lang %{name}-1

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 109 polkitd
%useradd -u 109 -s /bin/false -c "polkitd pseudo user" -g polkitd polkitd

%postun
if [ "$1" = "0" ]; then
    %userremove polkitd
    %groupremove polkitd
fi

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files -f %{name}-1.lang
%defattr(644,root,root,755)
%doc AUTHORS README

# The file %{_bindir}/pkexec must be owned by root and
# mode 4755 (setuid root binary)
%attr(4755,root,root) %{_bindir}/pkexec

%attr(755,root,root) %{_bindir}/pkaction
%attr(755,root,root) %{_bindir}/pkcheck
%attr(755,root,root) %{_bindir}/pkttyagent

# The file %{_libexecdir}/polkit-agent-helper-1 must be owned
# root and have mode 4755 (setuid root binary)
%attr(4755,root,root) %{_libexecdir}/polkit-agent-helper-1

%dir %{_libexecdir}
%attr(755,root,root) %{_libexecdir}/polkitd

# The directory /etc/polkit-1/rules.d must be owned
# by user 'polkitd' and have mode 700
%attr(700,polkitd,root) /etc/polkit-1/rules.d

%dir /etc/polkit-1
/etc/polkit-1/rules.d/50-default.rules

%dir %{_datadir}/polkit-1
%dir %{_datadir}/polkit-1/actions
%{_datadir}/polkit-1/actions/org.freedesktop.policykit.policy

# The directory %{_datadir}/polkit-1/rules.d must be owned
# by user 'polkitd' and have mode 700
%attr(700,polkitd,root) %dir %{_datadir}/polkit-1/rules.d

/etc/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
/etc/pam.d/polkit-1
%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit1.service
%{systemdunitdir}/polkit.service

%{_mandir}/man1/pkaction.1*
%{_mandir}/man1/pkcheck.1*
%{_mandir}/man1/pkexec.1*
%{_mandir}/man1/pkttyagent.1*
%{_mandir}/man8/polkit.8*
%{_mandir}/man8/polkitd.8*

%files libs
%defattr(644,root,root,755)
# notes which license applies to which package part, AFL text (and GPL text copy)
%doc COPYING
%attr(755,root,root) %ghost %{_libdir}/libpolkit-agent-1.so.?
%attr(755,root,root) %ghost %{_libdir}/libpolkit-gobject-1.so.?
%attr(755,root,root) %{_libdir}/libpolkit-agent-1.so.*.*.*
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so.*.*.*
%{_libdir}/girepository-1.0/*.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libpolkit-agent-1.so
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so
%{_includedir}/polkit-1
%{_pkgconfigdir}/polkit-agent-1.pc
%{_pkgconfigdir}/polkit-gobject-1.pc
%{_datadir}/gir-1.0/Polkit-1.0.gir
%{_datadir}/gir-1.0/PolkitAgent-1.0.gir

