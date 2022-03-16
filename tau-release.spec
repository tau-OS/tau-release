# Core
%define release_name Prerelease
%define dist_version 36
%define codename Martin Perl

Summary:        tauOS release files
Name:           tau-release
Version:        1.0.0
Release:        2
License:        GPLv3
URL:            https://tauos.co
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Provides:       fedora-release = %{dist_version}-%{release}
Provides:       fedora-release-variant = %{dist_version}-%{release}
Provides:       system-release = %{dist_version}-%{release}
Provides:       system-release(%{dist_version}) = %{dist_version}-%{release}
Provides:       base-module(platform:f%{dist_version}) = %{dist_version}-%{release}
Conflicts:      generic-release

Requires:       tau-release-identity
Requires:       tau-release-ostree-desktop
Obsoletes:      fedora-release-ostree-counting < 35-0.32

# We could use the Third-party repos (https://src.fedoraproject.org/rpms/fedora-release/blob/f35/f/fedora-release.spec#_585)

%description
tauOS release files such as various /etc/ files that define the release

%package identity
Summary:        Package providing the identity for tauOS
Provides:       fedora-release-identity = %{dist_version}-%{release}
Provides:       tau-release-identity-gnome  = %{dist_version}-%{release}
Conflicts:      fedora-release-identity
%description identity
Provides the necessary files for a tauOS installation

%package identity-kde
Summary:        Package providing the identity for tauOS Dragon
RemovePathPostfixes: .kde
Provides:       fedora-release-identity = %{dist_version}-%{release}
Conflicts:      fedora-release-identity

%description identity-kde
Provides the necessary files for tauOS KDE Dragon

%package identity-mate
Summary:        Package providing the identity for tauOS Cimarrón
RemovePathPostfixes: .mate
Provides:       fedora-release-identity = %{dist_version}-%{release}
Conflicts:      fedora-release-identity

%description identity-mate
Provides the necessary files for tauOS Cimarrón

%package ostree-desktop
Summary:        Configuration package for rpm-ostree to add rpm-ostree polkit rules

%description ostree-desktop
Configuration package for rpm-ostree to add rpm-ostree polkit rules

%prep
%setup -q
%build

%install
install -d %{buildroot}%{_prefix}/lib
echo "tauOS release %{version} (%{release_name})" > %{buildroot}%{_prefix}/lib/tau-release
# Symlink the -release files
install -d %{buildroot}%{_sysconfdir}
ln -s ../usr/lib/tau-release %{buildroot}%{_sysconfdir}/tau-release
ln -s tau-release %{buildroot}%{_sysconfdir}/redhat-release
ln -s tau-release %{buildroot}%{_sysconfdir}/system-release
ln -s tau-release %{buildroot}%{_sysconfdir}/fedora-release

# Create the common os-release file
%{lua:
  function starts_with(str, start)
   return str:sub(1, #start) == start
  end
}

cat << EOF >> os-release
NAME="tauOS"
VERSION="%{version} %{release_name}"
ID=tau
ID_LIKE=fedora
VERSION_ID=%{dist_version}
VERSION_CODENAME="%{codename}"
PLATFORM_ID="platform:f%{dist_version}"
PRETTY_NAME="tauOS %{version} \"%{codename}\" (%{release_name})"
ANSI_COLOR="1;34"
LOGO=tau-logo
HOME_URL="https://tauos.co"
DOCUMENTATION_URL="https://wiki.tauos.co"
SUPPORT_URL="https://github.com/tauLinux/meta/discussions"
BUG_REPORT_URL="https://github.com/tauLinux/meta/issues"
EOF

# Create the common /etc/issue
echo "\S" > %{buildroot}%{_prefix}/lib/issue
echo "Kernel \r on an \m (\l)" >> %{buildroot}%{_prefix}/lib/issue
echo >> %{buildroot}%{_prefix}/lib/issue
ln -s ../usr/lib/issue %{buildroot}%{_sysconfdir}/issue

# Create /etc/issue.net
echo "\S" > %{buildroot}%{_prefix}/lib/issue.net
echo "Kernel \r on an \m (\l)" >> %{buildroot}%{_prefix}/lib/issue.net
ln -s ../usr/lib/issue.net %{buildroot}%{_sysconfdir}/issue.net

# Create /etc/issue.d
mkdir -p %{buildroot}%{_sysconfdir}/issue.d

cp -p os-release %{buildroot}%{_prefix}/lib/os-release

# Modify os-release for different editions

# KDE
cp -p os-release \
      %{buildroot}%{_prefix}/lib/os-release.kde
echo "VARIANT=\"Dragon\"" >> %{buildroot}%{_prefix}/lib/os-release.kde
echo "VARIANT_ID=kde" >> %{buildroot}%{_prefix}/lib/os-release.kde
sed -i -e "s|tauOS %{version}|tauOS Dragon %{version}|g" %{buildroot}%{_prefix}/lib/os-release.kde

# MATE
cp -p os-release \
      %{buildroot}%{_prefix}/lib/os-release.mate
echo "VARIANT=\"Cimarrón\"" >> %{buildroot}%{_prefix}/lib/os-release.mate
echo "VARIANT_ID=mate" >> %{buildroot}%{_prefix}/lib/os-release.mate
sed -i -e "s|tauOS %{version}|tauOS Cimarrón %{version}|g" %{buildroot}%{_prefix}/lib/os-release.mate

# TODO you could use a custom codename but idc

# Override the list of enabled gnome-shell extensions
install -Dm0644 80-tau.preset -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 org.gnome.shell.gschema.override -t %{buildroot}%{_datadir}/glib-2.0/schemas/

# Override certain Gnome settings
install -Dm0644 org.gnome.desktop.gschema.override -t %{buildroot}%{_datadir}/glib-2.0/schemas/

# Install rpm-ostree polkit rules
install -Dm0644 org.projectatomic.rpmostree1.rules -t %{buildroot}%{_datadir}/polkit-1/rules.d/

# Statically enable rpm-ostree-countme timer
install -dm0755 %{buildroot}%{_unitdir}/timers.target.wants/
ln -snf %{_unitdir}/rpm-ostree-countme.timer %{buildroot}%{_unitdir}/timers.target.wants/


# Create the symlink for /etc/os-release
ln -s ../usr/lib/os-release %{buildroot}%{_sysconfdir}/os-release

# Set up the dist tag macros. These are gonna be the same as Fedora, for compatibility
install -d -m 755 %{buildroot}%{_rpmconfigdir}/macros.d
cat >> %{buildroot}%{_rpmconfigdir}/macros.d/macros.dist << EOF
# dist macros.

%%__bootstrap         ~bootstrap
%%fedora              %{dist_version}
%%fc%{dist_version}                1
%%dist                %%{!?distprefix0:%%{?distprefix}}%%{expand:%%{lua:for i=0,9999 do print("%%{?distprefix" .. i .."}") end}}.fc%%{fedora}%%{?with_bootstrap:%{__bootstrap}}
EOF


# Install licenses
mkdir -p licenses
install -pm 0644 LICENSE licenses/LICENSE


# Default system wide
install -Dm0644 85-display-manager.preset -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 90-default.preset -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 90-default-user.preset -t %{buildroot}%{_prefix}/lib/systemd/user-preset/
# The same file is installed in two places with identical contents
install -Dm0644 99-default-disable.preset -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 99-default-disable.preset -t %{buildroot}%{_prefix}/lib/systemd/user-preset/


%files
%license licenses/LICENSE
%{_prefix}/lib/os-release
%{_prefix}/lib/tau-release
%{_sysconfdir}/os-release
%{_sysconfdir}/tau-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release
%attr(0644,root,root) %{_prefix}/lib/issue
%config(noreplace) %{_sysconfdir}/issue
%attr(0644,root,root) %{_prefix}/lib/issue.net
%config(noreplace) %{_sysconfdir}/issue.net
%dir %{_sysconfdir}/issue.d
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir %{_prefix}/lib/systemd/user-preset/
%{_prefix}/lib/systemd/user-preset/90-default-user.preset
%{_prefix}/lib/systemd/user-preset/99-default-disable.preset
%dir %{_prefix}/lib/systemd/system-preset/
%{_prefix}/lib/systemd/system-preset/80-tau.preset
%{_prefix}/lib/systemd/system-preset/85-display-manager.preset
%{_prefix}/lib/systemd/system-preset/90-default.preset
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset

%files identity
%{_datadir}/glib-2.0/schemas/org.gnome.shell.gschema.override
%{_datadir}/glib-2.0/schemas/org.gnome.desktop.gschema.override
%{_unitdir}/timers.target.wants/rpm-ostree-countme.timer

%files identity-kde
%{_prefix}/lib/os-release.kde
%{_unitdir}/timers.target.wants/rpm-ostree-countme.timer

%files identity-mate
%{_prefix}/lib/os-release.mate
%{_unitdir}/timers.target.wants/rpm-ostree-countme.timer

%files ostree-desktop
%attr(0644,root,root) %{_prefix}/share/polkit-1/rules.d/org.projectatomic.rpmostree1.rules

%changelog
%autochangelog
