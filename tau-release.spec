# Core
%define release_name 1Pre
%define dist_version 37
%define codename Neko

Summary:        tauOS release files
Name:           tau-release
Version:        1.1
Release:        2
License:        GPLv3
URL:            https://tauos.co

Source0:        README.md
Source1:        LICENSE

# Styles
Source2:        gtk.css
Source3:        flatpak-global

# Overrides
Source11:       org.gnome.desktop.gschema.override
Source12:       org.gnome.mutter.gschema.override
Source13:       org.gnome.shell.gschema.override
Source14:       org.projectatomic.rpmostree1.rules

# Presets
Source21:       80-tau.preset
Source22:       85-display-manager.preset
Source23:       90-default-user.preset
Source24:       90-default.preset
Source25:       99-default-disable.preset

# GDM
Source26:       00-gdm-settings

# Flatpak
Source27:       https://flathub.org/repo/flathub.flatpakrepo
Source28:       https://repo.tauos.co/catalogue.flatpakrepo

BuildRequires:  systemd-rpm-macros

BuildArch:      noarch
Provides:       fedora-release = %{dist_version}-%{release}
Provides:       fedora-release-variant = %{dist_version}-%{release}
Provides:       system-release = %{dist_version}
Provides:       system-release(%{dist_version}) = %{dist_version}
Provides:       base-module(platform:f%{dist_version}) = %{dist_version}
Conflicts:      generic-release

Obsoletes:      fedora-release-ostree-counting <= 37

# We could use the Third-party repos (https://src.fedoraproject.org/rpms/fedora-release/blob/f36/f/fedora-release.spec#_589)

%description
Generic files and overrides for all tauOS variants

%package core
Summary:        tauOS Release Files
RemovePathPostfixes: .core

%description core
Generic files and overrides for Core-specific tauOS Variants

%package desktop
Summary:        tauOS Release Files
RemovePathPostfixes: .desktop
Provides:       fedora-release-identity = %{dist_version}-%{release}
Provides:       tau-release-identity-gnome  = %{dist_version}-%{release}
Provides:       tau-release-identity  = %{dist_version}-%{release}
Conflicts:      fedora-release-identity

%description desktop
Generic files and overrides for Desktop-specific tauOS Variants

%package server
Summary:        tauOS Release Files
RemovePathPostfixes: .server

%description server
Generic files and overrides for Server-specific tauOS Variants

%prep

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
PRETTY_NAME="tauOS %{version} (%{release_name})"
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

# Modify os-release for different variants
cp -p os-release %{buildroot}%{_prefix}/lib/os-release.core
echo "VARIANT=\"Core\"" >> %{buildroot}%{_prefix}/lib/os-release.core
echo "VARIANT_ID=core" >> %{buildroot}%{_prefix}/lib/os-release.core
cp -p os-release %{buildroot}%{_prefix}/lib/os-release.desktop
echo "VARIANT=\"Desktop\"" >> %{buildroot}%{_prefix}/lib/os-release.desktop
echo "VARIANT_ID=desktop" >> %{buildroot}%{_prefix}/lib/os-release.desktop
cp -p os-release %{buildroot}%{_prefix}/lib/os-release.server
echo "VARIANT=\"Server\"" >> %{buildroot}%{_prefix}/lib/os-release.server
echo "VARIANT_ID=server" >> %{buildroot}%{_prefix}/lib/os-release.server

rm %{buildroot}%{_prefix}/lib/os-release

# Override the list of enabled gnome-shell extensions
install -Dm0644 %SOURCE21 -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %SOURCE13 -t %{buildroot}%{_datadir}/glib-2.0/schemas/

# Install GNOME Wallpapers (being done here in case we do custom version wallpapers and need variables and shit)
/bin/echo '[org.gnome.desktop.background]' >> \
    %SOURCE11
/bin/echo "picture-uri='file://%{_datadir}/backgrounds/tauos/tau-light.png'" >> \
    %SOURCE11
/bin/echo "picture-uri-dark='file://%{_datadir}/backgrounds/tauos/tau-dark.png'" >> \
    %SOURCE11

# Override certain Gnome settings
install -Dm0644 %SOURCE11 -t %{buildroot}%{_datadir}/glib-2.0/schemas/
install -Dm0644 %SOURCE12 -t %{buildroot}%{_datadir}/glib-2.0/schemas/

# Install rpm-ostree polkit rules
install -Dm0644 %SOURCE14 -t %{buildroot}%{_datadir}/polkit-1/rules.d/

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


# Install licenses and documentation
mkdir -p licenses
install -pm 0644 %SOURCE1 licenses/LICENSE

install -pm 0644 %SOURCE0 README.md

# Default system wide
install -Dm0644 %SOURCE22 -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %SOURCE24 -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %SOURCE23 -t %{buildroot}%{_prefix}/lib/systemd/user-preset/
# The same file is installed in two places with identical contents
install -Dm0644 %SOURCE25 -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %SOURCE25 -t %{buildroot}%{_prefix}/lib/systemd/user-preset/

# Install GDM settings
install -Dm0644 %SOURCE26 -t %{buildroot}%{_sysconfdir}/dconf/db/gdm.d/

# Install the GTK CSS and Flatpak Adjustments
mkdir -p %{buildroot}%{_sysconfdir}/skel/.config/gtk-4.0
install -Dm0644 %SOURCE2 -t %{buildroot}%{_sysconfdir}/skel/.config/gtk-4.0/

install -d %{buildroot}%{_sysconfdir}/skel/.local/share/flatpak/overrides
install -d %{buildroot}%{_sysconfdir}/flatpak
install -Dm0644 %SOURCE3 -T %{buildroot}%{_sysconfdir}/flatpak/global-overrides
ln -s ../etc/flatpak/global-overrides %{buildroot}%{_sysconfdir}/skel/.local/share/flatpak/overrides/global

# Install flatpak remotes
mkdir -p %{buildroot}%{_sysconfdir}/flatpak/remotes.d
install -Dm0644 %SOURCE27 -t %{buildroot}%{_sysconfdir}/flatpak/remotes.d
install -Dm0644 %SOURCE28 -t %{buildroot}%{_sysconfdir}/flatpak/remotes.d

# Ghost file IG
touch SERVER.md
echo "Placeholder - to be replaced" > SERVER.md
touch CORE.md
echo "Placeholder - to be replaced" > CORE.md

%files
%doc README.md
%license licenses/LICENSE
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
%{_unitdir}/timers.target.wants/rpm-ostree-countme.timer
%attr(0644,root,root) %{_prefix}/share/polkit-1/rules.d/org.projectatomic.rpmostree1.rules
%{_sysconfdir}/dconf/db/gdm.d/00-gdm-settings

%files desktop
%{_prefix}/lib/os-release.desktop
%{_prefix}/lib/tau-release
%{_sysconfdir}/os-release
%{_sysconfdir}/tau-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release
%{_datadir}/glib-2.0/schemas/org.gnome.shell.gschema.override
%{_datadir}/glib-2.0/schemas/org.gnome.desktop.gschema.override
%{_datadir}/glib-2.0/schemas/org.gnome.mutter.gschema.override
%{_sysconfdir}/skel/.config/gtk-4.0/gtk.css
%dir %{_sysconfdir}/skel/.local/share/flatpak/overrides
%dir %{_sysconfdir}/flatpak
%{_sysconfdir}/skel/.local/share/flatpak/overrides/global
%{_sysconfdir}/flatpak/global-overrides
%{_sysconfdir}/flatpak/remotes.d/flathub.flatpakrepo
%{_sysconfdir}/flatpak/remotes.d/catalogue.flatpakrepo

%files server
%doc SERVER.md
%{_prefix}/lib/os-release.server
%{_prefix}/lib/tau-release
%{_sysconfdir}/os-release
%{_sysconfdir}/tau-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release

%files core
%doc CORE.md
%{_prefix}/lib/os-release.core
%{_prefix}/lib/tau-release
%{_sysconfdir}/os-release
%{_sysconfdir}/tau-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release

%changelog
* Mon Oct 3 2022 Jaiden Riordan <jade@fyralabs.com> - 1.1-2
- Bump for F37
- Kill codenames

* Sun May 22 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.11
- Introduce Core variant
- VARIANT and VARIANT_ID in os-release

* Sat May 21 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.10
- Fix Flatpaks again

* Wed May 18 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.7
- Completely reorganise packages

* Mon May 9 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.6
- Add user-themes to extensions

* Sat May 7 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.5
- Change fonts

* Thu Apr 28 2022 Lains <lainsce@airmail.cc> - 1.1-1.4
- Update window control override to reflect new design

* Sat Apr 23 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.3
- Add Hydrogen icon theme

* Sat Apr 23 2022 Jamie Murphy <jamie@fyralabs.com> - 1.1-1.2
- Update keybindings

* Wed Mar 23 2022 Jamie Lee <jamie@innatical.com> - 1.1-0
- Update for Fedora 36

* Tue Aug 10 2021 Tomas Hrcka <thrcka@redhat.com> - 35-0.16
- F35 branched form rawhide
