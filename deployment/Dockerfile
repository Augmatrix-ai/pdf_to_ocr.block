FROM ubuntu:focal-20230605

# Set the timezone without interaction
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    zip \
    python3-pip \
    python3.8 \
    pkg-config \
    build-essential \
    vim \
    curl \
	git \
    screen && \
    apt-get install -y tzdata && \

    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Set the timezone without interaction
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

# Copy files
COPY pdf_to_ocr.block /pdf_to_ocr.block
COPY requirments.txt .
COPY entrypoint.sh .

# Install Python packages
RUN pip3 install -r requirments.txt
RUN pip install git+https://github.com/Augmatrix-ai/augmatrixOS.git
# Set permissions and convert line endings
RUN chmod +x entrypoint.sh && \
    sed -i -e 's/\r$//' entrypoint.sh

# Set the entry point
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["sleep", "infinity"]

