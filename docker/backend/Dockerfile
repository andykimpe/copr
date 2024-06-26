FROM registry.fedoraproject.org/fedora:39
MAINTAINER copr-devel@lists.fedorahosted.org

ARG ADDITIONAL_COPR_REPOSITORIES="goddabrouquita8280/copr-mock-testing"

ENV export LANG=en_US.UTF-8
ENV PYTHONPATH="/usr/share/copr/"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux \
    LANG=en_US.UTF-8

# base packages
RUN set -ex ; \
    test -z "${ADDITIONAL_COPR_REPOSITORIES}" \
        || dnf -y install dnf-plugins-core \
        && for repo in $ADDITIONAL_COPR_REPOSITORIES ; do dnf -y copr enable $repo; done ; \
    dnf -y update && \
    dnf -y install htop \
                   make \
                   wget \
                   net-tools \
                   iputils \
                   vim \
                   mlocate \
                   git \
                   sudo \
                   openssh-server \
                   resalloc \
                   psmisc \
                   nginx \
                   python3-ipdb \
                   findutils \
                   tini \
# to get more entropy for generation of gpg keys
                   rng-tools \
# for unbuffer package
                   expect \
    && dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-39.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-39.noarch.rpm -y \
    && dnf install mock-rpmfusion-nonfree bind-utils -y \
    && sed -i 's|epel-9-x86_64.cfg|alma+epel-9-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-9-x86_64.cfg \
    && sed -i 's|epel-8-x86_64.cfg|alma+epel-8-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-8-x86_64.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_free.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_nonfree.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && sed -i 's|epel-next-9-x86_64.cfg|epel-next-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && sed -i 's|epel-next+rpmfusion_free-9-x86_64.cfg|epel-next+rpmfusion_free-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && dnf -y install copr-backend \
    && dnf clean all

# needed to be able to ping
RUN setcap cap_net_raw,cap_net_admin+p /usr/bin/ping

# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q

# setup root user
RUN echo 'root:passwd' | chpasswd && chmod 700 /root /root/.ssh

# setup copr user
RUN set -x ; \
    echo 'copr:passwd' | chpasswd && \
    echo 'copr ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    mkdir -p /home/copr/.ssh && chmod 700 /home/copr /home/copr/.ssh && \
    ssh-keygen -f /home/copr/.ssh/id_rsa -N '' -q -C copr@locahost && \
    touch /home/copr/.ssh/authorized_keys && chmod 600 /home/copr/.ssh/authorized_keys && \
    cat /home/copr/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    cat /home/copr/.ssh/id_rsa.pub >> /home/copr/.ssh/authorized_keys && \
    chown copr:copr -R /home/copr

# system setup for copr-backend
RUN usermod -a -G mock copr

# copy filesystem setup and setup ownership and permissions
COPY files/ /
RUN chmod 700 /root && \
    chmod 700 /home/copr && \
    chmod 400 /home/copr/.ssh/id_rsa && \
    chmod 600 /home/copr/.ssh/id_rsa.pub && \
    chown -R copr:copr /home/copr

# Copr user needs permissions for /bin/sign.  We drop the setuid bit here as in
# container scenario it is not desired.  We use the downstream-only option
# allow-unprivileged-ports option: https://github.com/openSUSE/obs-sign/pull/36
RUN chmod 0755 /usr/bin/sign

# entrypoint needs to have write access here (group=0)
RUN chown copr:root /etc/sign.conf && \
    chmod 0660 /etc/sign.conf

# Not sure why the directory wasn't created automatically
RUN mkdir /var/lock/copr-backend
RUN chown copr:copr /var/lock/copr-backend
    
RUN sed -i 's|backend_httpd|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr/copr-be.conf
RUN sed -i 's|localhost|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr/copr-be.conf
RUN sed -i 's|frontend|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr/copr-be.conf
RUN sed -i 's|distgit-httpd|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr/copr-be.conf

# using /dev/urandom is a hack just for devel, /dev/hwrandom or /dev/hwrng should be used in production
RUN rngd -r /dev/urandom

USER copr

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run-backend"]
