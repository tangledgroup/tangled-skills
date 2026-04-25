---
name: libcurl-tutorial-reference
description: Complete programming tutorial for libcurl C library covering initialization, easy interface, multi interface, MIME API, cookie handling, proxy configuration, and HTTP methods.
version: "8.19.0"
---

# libcurl Tutorial Reference

## Building

### Compiling the Program

```bash
$ curl-config --cflags
```

### Linking the Program with libcurl

```bash
$ curl-config --libs
```

### Check for SSL Support

```bash
$ curl-config --feature
# Output includes "SSL" if SSL is enabled
```

## Global Initialization

Must be called exactly once per application:

```c
#include <curl/curl.h>

int main(void) {
    CURLcode res;

    // Initialize all libcurl subsystems
    curl_global_init(CURL_GLOBAL_ALL);

    // ... use libcurl ...

    // Cleanup (must match init, called once at exit)
    curl_global_cleanup();

    return 0;
}
```

Options for `curl_global_init()`:
- `CURL_GLOBAL_ALL` - Initialize all subsystems
- `CURL_GLOBAL_WIN32` - Windows socket initialization only
- `CURL_GLOBAL_SSL` - SSL library initialization only

## Easy Interface (Single Transfer)

### Basic GET Request

```c
#include <stdio.h>
#include <stdlib.h>
#include <curl/curl.h>

static size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    size_t total = size * nmemb;
    fwrite(ptr, size, nmemb, (FILE*)userdata);
    return total;
}

int main(void) {
    CURL *curl;
    CURLcode res;
    FILE *outfile;

    curl_global_init(CURL_GLOBAL_ALL);

    curl = curl_easy_init();
    if (curl) {
        outfile = fopen("output.html", "wb");
        curl_easy_setopt(curl, CURLOPT_URL, "https://example.com/");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, outfile);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n",
                    curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
        fclose(outfile);
    }

    curl_global_cleanup();
    return 0;
}
```

### POST Request with JSON

```c
static size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    return fwrite(ptr, size, nmemb, (FILE*)userdata);
}

int main(void) {
    CURL *curl;
    CURLcode res;
    FILE *outfile;
    struct curl_slist *headers = NULL;
    const char *data = "{\"name\":\"test\",\"value\":42}";

    curl_global_init(CURL_GLOBAL_ALL);

    curl = curl_easy_init();
    if (curl) {
        outfile = fopen("response.txt", "wb");

        // Set headers
        headers = curl_slist_append(headers, "Content-Type: application/json");
        headers = curl_slist_append(headers, "Accept: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, "https://api.example.com/endpoint");
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, outfile);

        res = curl_easy_perform(curl);

        // Cleanup
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        fclose(outfile);
    }

    curl_global_cleanup();
    return 0;
}
```

### Multipart Form Upload (MIME API)

```c
int main(void) {
    CURL *curl;
    CURLcode res;
    curl_mime *multipart;
    curl_mimepart *part;

    curl_global_init(CURL_GLOBAL_ALL);

    curl = curl_easy_init();
    if (curl) {
        // Create multipart body
        multipart = curl_mime_init(curl);

        // Text field
        part = curl_mime_addpart(multipart);
        curl_mime_name(part, "username");
        curl_mime_data(part, "john_doe", CURL_ZERO_TERMINATED);

        // File upload
        part = curl_mime_addpart(multipart);
        curl_mime_name(part, "avatar");
        curl_mime_filename(part, "profile.jpg");
        curl_mime_type(part, "image/jpeg");
        curl_mime_filedata(part, "/path/to/profile.jpg");

        curl_easy_setopt(curl, CURLOPT_URL, "https://api.example.com/upload");
        curl_easy_setopt(curl, CURLOPT_MIMEPOST, multipart);

        res = curl_easy_perform(curl);

        // Cleanup
        curl_mime_free(multipart);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### Email via SMTP (MIME API)

```c
int main(void) {
    CURL *curl;
    curl_mime *message;
    curl_mimepart *part;
    struct curl_slist *headers = NULL;

    curl_global_init(CURL_GLOBAL_ALL);

    curl = curl_easy_init();
    if (curl) {
        message = curl_mime_init(curl);

        // Plain text part
        part = curl_mime_addpart(message);
        curl_mime_name(part, "body");
        curl_mime_data(part, "Hello, this is the email body.", CURL_ZERO_TERMINATED);
        curl_mime_type(part, "text/plain");

        // Attachment
        part = curl_mime_addpart(message);
        curl_mime_filename(part, "attachment.pdf");
        curl_mime_filedata(part, "/path/to/document.pdf");
        curl_mime_encoder(part, "base64");

        // Email headers
        headers = curl_slist_append(headers, "From: sender@example.com");
        headers = curl_slist_append(headers, "To: recipient@example.com");
        headers = curl_slist_append(headers, "Subject: Test Email");

        curl_easy_setopt(curl, CURLOPT_URL, "smtp://smtp.example.com");
        curl_easy_setopt(curl, CURLOPT_MAIL_FROM, "sender@example.com");
        curl_easy_setopt(curl, CURLOPT_MAIL_RCPT, "recipient@example.com");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_MIMEPOST, message);

        curl_easy_perform(curl);

        curl_mime_free(message);
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### HTTP Authentication

```c
int main(void) {
    CURL *curl;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        // Basic auth
        curl_easy_setopt(curl, CURLOPT_URL, "https://secure.example.com/");
        curl_easy_setopt(curl, CURLOPT_USERPWD, "username:password");
        curl_easy_setopt(curl, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);

        // Digest auth
        curl_easy_setopt(curl, CURLOPT_HTTPAUTH, CURLAUTH_DIGEST);

        // NTLM auth
        curl_easy_setopt(curl, CURLOPT_HTTPAUTH, CURLAUTH_NTLM);

        // Let libcurl choose best method
        curl_easy_setopt(curl, CURLOPT_HTTPAUTH, CURLAUTH_ANY);

        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### Proxy Configuration

```c
int main(void) {
    CURL *curl;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        // HTTP proxy
        curl_easy_setopt(curl, CURLOPT_PROXY, "proxy.example.com:8080");
        curl_easy_setopt(curl, CURLOPT_PROXYUSERPWD, "user:pass");

        // SOCKS5 proxy
        curl_easy_setopt(curl, CURLOPT_PROXYTYPE, CURLPROXY_SOCKS5);
        curl_easy_setopt(curl, CURLOPT_PROXY, "socks5://proxy.example.com:1080");

        // Disable proxy (even if environment variables are set)
        curl_easy_setopt(curl, CURLOPT_PROXY, "");

        // HTTP proxy tunneling for HTTPS
        curl_easy_setopt(curl, CURLOPT_HTTPPROXYTUNNEL, 1L);

        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### Cookie Handling

```c
int main(void) {
    CURL *curl;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        // Enable cookie parsing and load from file
        curl_easy_setopt(curl, CURLOPT_COOKIEFILE, "cookies.txt");

        // Save cookies to jar on cleanup
        curl_easy_setopt(curl, CURLOPT_COOKIEJAR, "cookies.txt");

        // Send specific cookies manually
        curl_easy_setopt(curl, CURLOPT_COOKIE, "session=abc123; path=/");

        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### FTP Transfer

```c
int main(void) {
    CURL *curl;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        // Upload to FTP
        curl_easy_setopt(curl, CURLOPT_URL, "ftp://ftp.example.com/remote.txt");
        curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
        curl_easy_setopt(curl, CURLOPT_READDATA, infile);

        // Download from FTP
        curl_easy_setopt(curl, CURLOPT_URL, "ftp://ftp.example.com/file.txt");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, outfile);

        // Custom FTP commands before transfer
        struct curl_slist *commands = NULL;
        commands = curl_slist_append(commands, "DELE oldfile.txt");
        curl_easy_setopt(curl, CURLOPT_QUOTE, commands);

        // FTPS (FTP over SSL)
        curl_easy_setopt(curl, CURLOPT_URL, "ftps://secure.server.com/file.txt");
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);

        curl_easy_perform(curl);

        curl_slist_free_all(commands);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### URL Encoding/Decoding

```c
int main(void) {
    CURL *curl;
    char *urlencoded;
    char *decoded;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        // Encode a string for URL usage
        urlencoded = curl_easy_escape(curl, "hello world & more", 0);
        printf("Encoded: %s\n", urlencoded);
        curl_free(urlencoded);

        // Decode a URL-encoded string
        decoded = curl_easy_unescape(curl, "hello%20world%20%26%20more", 0, NULL);
        printf("Decoded: %s\n", decoded);
        curl_free(decoded);

        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}
```

### Version Information

```c
int main(void) {
    curl_global_init(CURL_GLOBAL_ALL);

    // Simple version string
    printf("libcurl version: %s\n", curl_version());

    // Detailed version info
    struct curl_version_info *info = curl_version_info(CURLVERSION_NOW);
    printf("Version: %s\n", info->version);
    printf("SSL Version: %s\n", info->ssl_version);
    printf("Libz Version: %s\n", info->libz_version);
    printf("Protocols: ");
    for (int i = 0; info->protocols[i]; i++) {
        printf("%s ", info->protocols[i]);
    }
    printf("\n");

    curl_global_cleanup();
    return 0;
}
```

## Common Callback Prototypes

### Write Callback

```c
size_t write_callback(void *buffer, size_t size, size_t nmemb, void *userdata);
```

Returns the number of bytes actually processed. Must match the amount received or the transfer is aborted.

### Read Callback (for uploads)

```c
size_t read_callback(char *buffer, size_t size, size_t nitems, void *userdata);
```

Returns the number of bytes written to buffer, or 0 to signal end of upload.

### Progress Callback

```c
int progress_callback(void *clientp,
                      double dltotal, double dlnow,
                      double ultotal, double ulnow);
```

Return non-zero to abort the transfer. Values of -1 mean unknown.

### Debug Callback

```c
int debug_callback(CURL *handle, curl_infotype type,
                   char *data, size_t size, void *userptr);
```

Type values: CURLINFO_TEXT, CURLINFO_HEADER_IN, CURLINFO_HEADER_OUT,
CURLINFO_DATA_IN, CURLINFO_DATA_OUT, CURLINFO_SSL_DATA_IN, CURLINFO_SSL_DATA_OUT.

## Error Handling Pattern

```c
CURLcode res = curl_easy_perform(curl);
if (res != CURLE_OK) {
    fprintf(stderr, "curl failed with error %d: %s\n",
            res, curl_easy_strerror(res));
}
```

Or use `CURLOPT_ERRORBUFFER`:

```c
char errbuf[CURL_ERROR_SIZE];
curl_easy_setopt(curl, CURLOPT_ERRORBUFFER, errbuf);
curl_easy_perform(curl);
if (res != CURLE_OK) {
    fprintf(stderr, "Error: %s\n", errbuf);
}
```
