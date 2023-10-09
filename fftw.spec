Name:           fftw
Version:        3.3.10
Release:        1
Summary:        A Fast Fourier Transform library
# Generally, the code is under GPL but some headers are also under MIT or BSD:
License:        GPL-2.0-or-later AND MIT AND BSD-2-Clause
URL:            http://www.fftw.org
Source0:        %{name}-%{version}.tar.gz

%global quad 0
# Quad precision support only available on these arches
%ifarch %{ix86} x86_64
%global quad 1
%endif

# Names of precisions to (maybe) build
%global prec_names prec_name[0]=single;prec_name[1]=double;prec_name[2]=long;prec_name[3]=quad
# Number of precisions to build; sometimes quad is not possible
%global nprec 3
%if %{quad}
%global nprec 4
%endif

%description
FFTW is a C subroutine library for computing the Discrete Fourier
Transform (DFT) in one or more dimensions, of both real and complex
data, and of arbitrary input size.

%package libs
Summary:        FFTW run-time library
Provides:       fftw3 = %{version}-%{release}

# Pull in the actual libraries
Requires:       %{name}-libs-single%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs-double%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs-long%{?_isa} = %{version}-%{release}
%if %{quad}
Requires:       %{name}-libs-quad%{?_isa} = %{version}-%{release}
%endif

%description libs
This is a dummy package package, pulling in the individual FFTW
run-time libraries.


%package devel
Summary:        Headers, libraries and docs for the FFTW library
Requires:       pkgconfig
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Provides:       fftw3-devel%{?_isa} = %{version}-%{release}
Provides:       fftw3-devel = %{version}-%{release}

%description devel
FFTW is a C subroutine library for computing the Discrete Fourier
Transform (DFT) in one or more dimensions, of both real and complex
data, and of arbitrary input size.

This package contains header files and development libraries needed to
develop programs using the FFTW fast Fourier transform library.

%package libs-double
Summary:        FFTW library, double precision

%description libs-double
This package contains the FFTW library compiled in double precision.

%package libs-single
Summary:        FFTW library, single precision

%description libs-single
This package contains the FFTW library compiled in single precision.

%package libs-long
Summary:        FFTW library, long double precision 

%description libs-long
This package contains the FFTW library compiled in long double
precision.

%if %{quad}
%package libs-quad
Summary:        FFTW library, quadruple

%description libs-quad
This package contains the FFTW library compiled in quadruple
precision.
%endif

%package        static
Summary:        Static versions of the FFTW libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Provides:       fftw3-static%{?_isa} = %{version}-%{release}
Provides:       fftw3-static = %{version}-%{release}

%description static
The fftw-static package contains the statically linkable version of
the FFTW fast Fourier transform library.

%prep
%setup -q

%build

BASEFLAGS="--disable-doc --enable-shared --disable-dependency-tracking --enable-threads"
BASEFLAGS+=" --enable-openmp"

%prec_names

# Corresponding flags
prec_flags[0]=--enable-single
prec_flags[1]=--enable-double
prec_flags[2]=--enable-long-double
prec_flags[3]=--enable-quad-precision

%ifarch x86_64
# Enable SSE2 and AVX support for x86_64
for ((i=0; i<2; i++)) ; do
    prec_flags[i]+=" --enable-sse2 --enable-avx --enable-avx2"
done
%endif

%ifarch aarch64
# Compile support for NEON instructions
for ((i=0; i<2; i++)) ; do
    prec_flags[i]+=" --enable-neon"
done
BASEFLAGS+=" --enable-armv8-cntvct-el0"
%endif

# Loop over precisions
for ((iprec=0; iprec<%{nprec}; iprec++)) ; do
    mkdir -p ${prec_name[iprec]}${ver_name[iver]}
    cd ${prec_name[iprec]}${ver_name[iver]}
    ln -sf ../configure .
    %{configure} ${BASEFLAGS} ${prec_flags[iprec]}
    sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
    sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
    %make_build
    cd ..
done

%install
%prec_names

for((iprec=0;iprec<%{nprec};iprec++)) ; do
    make DESTDIR=%{buildroot} INSTALL_ROOT=%{buildroot} install -C ${prec_name[iprec]}
done

rm -f %{buildroot}%{_infodir}/dir
rm -f %{buildroot}%{_mandir}/man1/fftw*.1*
find %{buildroot} -name \*.la -delete

%post libs-single -p /sbin/ldconfig
%postun libs-single -p /sbin/ldconfig

%post libs-double -p /sbin/ldconfig
%postun libs-double -p /sbin/ldconfig

%post libs-long -p /sbin/ldconfig
%postun libs-long -p /sbin/ldconfig

%if %{quad}
%post libs-quad -p /sbin/ldconfig
%postun libs-quad -p /sbin/ldconfig
%endif

%files
%{_bindir}/fftw*-wisdom*

%files libs

%files libs-single
%license COPYING COPYRIGHT
%doc AUTHORS ChangeLog NEWS README* TODO
%{_libdir}/libfftw3f.so.*
%{_libdir}/libfftw3f_threads.so.*
%{_libdir}/libfftw3f_omp.so.*

%files libs-double
%license COPYING COPYRIGHT
%doc AUTHORS ChangeLog NEWS README* TODO
%{_libdir}/libfftw3.so.*
%{_libdir}/libfftw3_threads.so.*
%{_libdir}/libfftw3_omp.so.*

%files libs-long
%license COPYING COPYRIGHT
%doc AUTHORS ChangeLog NEWS README* TODO
%{_libdir}/libfftw3l.so.*
%{_libdir}/libfftw3l_threads.so.*
%{_libdir}/libfftw3l_omp.so.*

%if %{quad}
%files libs-quad
%license COPYING COPYRIGHT
%doc AUTHORS ChangeLog NEWS README* TODO
%{_libdir}/libfftw3q.so.*
%{_libdir}/libfftw3q_threads.so.*
%{_libdir}/libfftw3q_omp.so.*
%endif

%files devel
%{_includedir}/fftw3*
%dir %{_libdir}/cmake/fftw3/
%{_libdir}/cmake/fftw3/*.cmake
%{_libdir}/pkgconfig/fftw3*.pc
%{_libdir}/libfftw3*.so

%files static
%{_libdir}/libfftw3*.a
