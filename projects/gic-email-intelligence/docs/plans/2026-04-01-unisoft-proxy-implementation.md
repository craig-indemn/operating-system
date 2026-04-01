# Unisoft REST Proxy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a REST proxy that wraps the Unisoft WCF SOAP service (910 operations) via HTTP/JSON, running as a Windows Service on EC2.

**Architecture:** Single C# file (`UniProxy.cs`), compiled with `csc.exe` on a Windows EC2 (t3.small). HttpListener on port 5000 accepts JSON, translates to SOAP XML with correct DTO namespaces, calls via WCF channel (WSHttpBinding + WS-SecureConversation + ReliableSession), returns JSON. Token management and keepalive are automatic.

**Tech Stack:** C# / .NET Framework 4.8 / csc.exe / Windows Service / HttpListener / WCF

**Design doc:** `projects/gic-email-intelligence/artifacts/2026-04-01-unisoft-rest-proxy-design.md`

**Proven code reference:** `projects/gic-email-intelligence/research/unisoft-api/UniExplore.cs` (working WCF channel, 14 operations tested)

---

## Parallel Track Structure

Three independent tracks that can run in separate sessions:

| Track | What | Dependency | Session Can Start |
|-------|------|-----------|-------------------|
| **A: Proxy Code** | Write UniProxy.cs — all C# code | None (write locally, test on EC2) | Immediately |
| **B: Infrastructure** | EC2 downsize, Elastic IP, security group, env vars, service setup | None (AWS CLI) | Immediately |
| **C: Python Client** | Client library + integration test suite | Needs Track A + B complete for integration tests | Immediately for code, needs A+B for testing |

**Orchestrator responsibilities:**
- Launch Track A and Track B in parallel
- Launch Track C once A and B are both done (or start code-only tasks early)
- Final integration test requires all three tracks complete

---

## Track A: Proxy Code

All code lives in one file: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

Supporting file: `projects/gic-email-intelligence/unisoft-proxy/compile.ps1` (compile + deploy script)

### Task A1: Project scaffold + compile script

**Files:**
- Create: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`
- Create: `projects/gic-email-intelligence/unisoft-proxy/compile.ps1`

**Step 1: Create the minimal compilable C# file**

Write a C# file that compiles and prints "UniProxy starting" then exits. This validates the compile pipeline.

```csharp
using System;

class UniProxy
{
    static void Main(string[] args)
    {
        Console.WriteLine("UniProxy v0.1 starting...");
        Console.WriteLine("Press Ctrl+C to exit.");
    }
}
```

**Step 2: Create the compile + deploy PowerShell script**

This script uploads to S3, downloads on EC2, compiles with csc.exe, and reports status. This is the dev loop for the entire track.

```powershell
# compile.ps1 — run from Mac, deploys to EC2 via S3+SSM
# Usage: pwsh compile.ps1 [run|compile|deploy]

$S3Bucket = "indemn-assets"
$S3Key = "unisoft/UniProxy.cs"
$InstanceId = "i-0dc2563c9bc92aa0e"
$LocalFile = "$PSScriptRoot/UniProxy.cs"
$RemoteDir = "C:\unisoft"
$CscPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$References = "System.ServiceModel.dll", "System.Runtime.Serialization.dll", "System.ServiceProcess.dll", "System.Web.Extensions.dll", "System.Xml.dll"

# Upload
aws s3 cp $LocalFile "s3://$S3Bucket/$S3Key"

# Build JSON params for SSM
$refArgs = ($References | ForEach-Object { "/reference:$_" }) -join " "
$presigned = aws s3 presign "s3://$S3Bucket/$S3Key" --expires-in 300

# Commands: download, compile, optionally run
$cmds = @(
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12"
    "Invoke-WebRequest -Uri '$presigned' -OutFile '$RemoteDir\UniProxy.cs'"
    "& '$CscPath' /out:$RemoteDir\UniProxy.exe $refArgs $RemoteDir\UniProxy.cs 2>&1"
    "if (Test-Path '$RemoteDir\UniProxy.exe') { Write-Output 'COMPILED OK' } else { Write-Output 'COMPILE FAILED' }"
)

# Add run command if requested
if ($args[0] -eq "run") {
    $cmds += "& '$RemoteDir\UniProxy.exe' 2>&1"
}

$params = @{ commands = $cmds } | ConvertTo-Json
$params | Out-File /tmp/ssm-params.json

$cmdId = aws ssm send-command `
    --instance-ids $InstanceId `
    --document-name "AWS-RunPowerShellScript" `
    --parameters file:///tmp/ssm-params.json `
    --timeout-seconds 120 `
    --output text --query 'Command.CommandId'

Write-Host "SSM Command: $cmdId"
Write-Host "Waiting..."
Start-Sleep -Seconds 15

$result = aws ssm get-command-invocation `
    --command-id $cmdId `
    --instance-id $InstanceId `
    --output json | ConvertFrom-Json

Write-Host "Status: $($result.Status)"
Write-Host $result.StandardOutputContent
if ($result.StandardErrorContent) { Write-Host "STDERR: $($result.StandardErrorContent)" }
```

**Step 3: Test the compile pipeline**

Ensure EC2 is running (Track B may have started it, or start it here):
```bash
aws ec2 start-instances --instance-ids i-0dc2563c9bc92aa0e
# Wait for SSM online
```

Upload, compile, run:
```bash
# If pwsh not available, use the bash pattern from earlier sessions:
aws s3 cp projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs s3://indemn-assets/unisoft/UniProxy.cs
# Then SSM command to download + compile + run (same pattern as UniExplore.cs)
```

Expected: `UniProxy v0.1 starting...` and `COMPILED OK` in SSM output.

**Step 4: Commit**

```bash
git add projects/gic-email-intelligence/unisoft-proxy/
git commit -m "feat(unisoft-proxy): scaffold — minimal compilable C# + deploy script"
```

---

### Task A2: HTTP listener + health endpoint

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Add HttpListener with routing**

Add the HTTP listener that handles `GET /api/health` and `POST /api/soap/{op}` (stub). Include API key validation.

Key code to add:

```csharp
using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;

class UniProxy
{
    static string apiKey;
    static DateTime startTime;
    static int requestCount = 0;
    static DateTime lastRequestTime;
    static long maxRequestBytes;
    static SoapBridge bridge; // wired in Task A3

    static void Main(string[] args)
    {
        apiKey = Environment.GetEnvironmentVariable("PROXY_API_KEY") ?? "dev-key";
        int port = int.Parse(Environment.GetEnvironmentVariable("PROXY_PORT") ?? "5000");
        maxRequestBytes = long.Parse(Environment.GetEnvironmentVariable("PROXY_MAX_REQUEST_BYTES") ?? "5242880");
        startTime = DateTime.UtcNow;

        var listener = new HttpListener();
        listener.Prefixes.Add(string.Format("http://+:{0}/", port));
        listener.Start();
        Console.WriteLine("UniProxy listening on port " + port);

        while (true)
        {
            var ctx = listener.GetContext();
            ThreadPool.QueueUserWorkItem(_ => HandleRequest(ctx));
        }
    }

    static void HandleRequest(HttpListenerContext ctx)
    {
        try
        {
            string path = ctx.Request.Url.AbsolutePath.ToLower();
            // Preserve original case for operation name
            string rawPath = ctx.Request.Url.AbsolutePath;

            if (path == "/api/health")
            {
                int tokenAgeSec = bridge != null && bridge.TokenAcquiredTime > DateTime.MinValue
                    ? (int)(DateTime.UtcNow - bridge.TokenAcquiredTime).TotalSeconds : -1;
                string channelState = bridge != null ? (bridge.IsHealthy ? "healthy" : "faulted") : "not_started";
                string lastReq = lastRequestTime > DateTime.MinValue
                    ? "\"" + lastRequestTime.ToString("o") + "\"" : "null";
                WriteJson(ctx, 200, "{\"status\":\"ok\",\"uptime_seconds\":" +
                    (int)(DateTime.UtcNow - startTime).TotalSeconds +
                    ",\"requests\":" + requestCount +
                    ",\"token_age_seconds\":" + tokenAgeSec +
                    ",\"channel_state\":\"" + channelState + "\"" +
                    ",\"last_request_time\":" + lastReq + "}");
                return;
            }

            if (path == "/api/meta/operations")
            {
                // Return a message pointing to the WSDL — the proxy supports all 910 IIMSService operations
                WriteJson(ctx, 200, "{\"service\":\"IIMSService\",\"operations\":910," +
                    "\"usage\":\"POST /api/soap/{OperationName} with JSON body\"," +
                    "\"wsdl\":\"https://services.uat.gicunderwriters.co/management/imsservice.svc?singleWsdl\"}");
                return;
            }

            // API key check for all other endpoints
            string key = ctx.Request.Headers["X-Api-Key"];
            if (key != apiKey)
            {
                WriteJson(ctx, 401, "{\"error\":\"unauthorized\"}");
                return;
            }

            if (path.StartsWith("/api/soap/") && ctx.Request.HttpMethod == "POST")
            {
                // Request body size limit
                if (ctx.Request.ContentLength64 > maxRequestBytes)
                {
                    WriteJson(ctx, 413, "{\"error\":\"request_too_large\",\"max_bytes\":" + maxRequestBytes + "}");
                    return;
                }

                string opName = rawPath.Substring("/api/soap/".Length);
                Interlocked.Increment(ref requestCount);
                lastRequestTime = DateTime.UtcNow;
                // TODO: wire to SOAP bridge (Task A3)
                WriteJson(ctx, 501, "{\"error\":\"not_implemented\",\"operation\":\"" + opName + "\"}");
                return;
            }

            WriteJson(ctx, 404, "{\"error\":\"not_found\"}");
        }
        catch (Exception ex)
        {
            WriteJson(ctx, 500, "{\"error\":\"proxy_error\",\"message\":\"" +
                ex.Message.Replace("\"", "\\\"") + "\"}");
        }
    }

    static void WriteJson(HttpListenerContext ctx, int status, string json)
    {
        byte[] buf = Encoding.UTF8.GetBytes(json);
        ctx.Response.StatusCode = status;
        ctx.Response.ContentType = "application/json";
        ctx.Response.ContentLength64 = buf.Length;
        ctx.Response.OutputStream.Write(buf, 0, buf.Length);
        ctx.Response.Close();
    }
}
```

**Step 2: Deploy and test**

Upload, compile, run via SSM. Then from Mac:

```bash
# Health check (no API key needed)
curl http://<EC2_IP>:5000/api/health

# Stub SOAP call (with API key)
curl -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceLOBs \
  -H "X-Api-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{}'

# Unauthorized
curl -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceLOBs \
  -H "Content-Type: application/json" -d '{}'
```

Expected: health returns 200 with JSON, soap stub returns 501, no key returns 401.

**Note:** Port 5000 must be open in the security group. Track B handles this, but if testing before Track B completes, temporarily open the port via:
```bash
aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 5000 --cidr <your-ip>/32
```

**Step 3: Commit**

```bash
git commit -m "feat(unisoft-proxy): HTTP listener with health endpoint and API key auth"
```

---

### Task A3: SOAP bridge — WCF channel + token management

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Add the SOAP bridge class**

This is the core — lifted from the proven `UniExplore.cs` code, restructured into a class with token management, keepalive, and channel resilience.

Key code to add:

```csharp
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Xml;

[ServiceContract(Namespace = "http://tempuri.org/")]
interface IIMSService
{
    [OperationContract(Action = "http://tempuri.org/IIMSService/GetToken",
                       ReplyAction = "http://tempuri.org/IIMSService/GetTokenResponse")]
    Message GetToken(Message request);

    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

class SoapBridge
{
    string soapUrl;
    string wsUser;
    string wsPass;
    string clientId;

    ChannelFactory<IIMSService> factory;
    IIMSService channel;
    int channelGeneration = 0;

    volatile string accessToken;
    object tokenLock = new object();
    SemaphoreSlim channelSem = new SemaphoreSlim(1, 1);

    Timer keepaliveTimer;
    Timer tokenRefreshTimer;

    public bool IsHealthy { get; private set; }
    public DateTime LastCallTime { get; private set; }
    public DateTime TokenAcquiredTime { get; private set; }

    public SoapBridge(string soapUrl, string wsUser, string wsPass, string clientId, bool skipCertValidation)
    {
        this.soapUrl = soapUrl;
        this.wsUser = wsUser;
        this.wsPass = wsPass;
        this.clientId = clientId;

        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        if (skipCertValidation)
            ServicePointManager.ServerCertificateValidationCallback =
                delegate(object s, X509Certificate c, X509Chain ch, SslPolicyErrors e) { return true; };
    }

    public void Start()
    {
        CreateFactory();
        OpenChannel();
        RefreshToken();

        // Keepalive every 5 min
        keepaliveTimer = new Timer(_ => Keepalive(), null,
            TimeSpan.FromMinutes(5), TimeSpan.FromMinutes(5));

        // Token refresh every 20 min
        tokenRefreshTimer = new Timer(_ => RefreshToken(), null,
            TimeSpan.FromMinutes(20), TimeSpan.FromMinutes(20));

        IsHealthy = true;
    }

    void CreateFactory()
    {
        var binding = new WSHttpBinding();
        binding.Security.Mode = SecurityMode.TransportWithMessageCredential;
        binding.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
        binding.Security.Message.EstablishSecurityContext = true;
        binding.ReliableSession.Enabled = true;
        binding.ReliableSession.InactivityTimeout = TimeSpan.FromMinutes(10);
        binding.MaxReceivedMessageSize = 50 * 1024 * 1024;
        binding.ReaderQuotas.MaxStringContentLength = 50 * 1024 * 1024;
        binding.ReaderQuotas.MaxArrayLength = 50 * 1024 * 1024;
        binding.OpenTimeout = TimeSpan.FromSeconds(30);
        binding.SendTimeout = TimeSpan.FromSeconds(60);
        binding.ReceiveTimeout = TimeSpan.FromSeconds(60);

        var endpoint = new EndpointAddress(soapUrl);
        factory = new ChannelFactory<IIMSService>(binding, endpoint);
        factory.Credentials.UserName.UserName = wsUser;
        factory.Credentials.UserName.Password = wsPass;
    }

    void OpenChannel()
    {
        channel = factory.CreateChannel();
        ((IClientChannel)channel).Open();
        Interlocked.Increment(ref channelGeneration);
    }

    void RecreateChannel()
    {
        try { ((IClientChannel)channel).Abort(); } catch { }
        OpenChannel();
        RefreshToken();
    }

    void RefreshToken()
    {
        // Acquire channel lock — timer-based calls must not race with API calls
        if (!channelSem.Wait(TimeSpan.FromSeconds(10)))
            return; // skip this refresh cycle if channel is busy

        try
        {
            string xml = SendMessage("GetToken", BuildGetTokenXml());
            string token = ExtractXmlValue(xml, "AccessToken");
            if (token != null)
            {
                lock (tokenLock) { accessToken = token; }
                TokenAcquiredTime = DateTime.UtcNow;
            }
        }
        catch { /* keepalive will catch channel issues */ }
        finally
        {
            channelSem.Release();
        }
    }

    void Keepalive()
    {
        try
        {
            RefreshToken();
            IsHealthy = true;
        }
        catch
        {
            IsHealthy = false;
            // RecreateChannel needs channelSem — acquire it
            if (channelSem.Wait(TimeSpan.FromSeconds(10)))
            {
                try { RecreateChannel(); } catch { }
                finally { channelSem.Release(); }
            }
        }
    }

    public string CallSoap(string opName, string requestXml)
    {
        if (!channelSem.Wait(TimeSpan.FromSeconds(30)))
            throw new TimeoutException("Channel busy");

        try
        {
            LastCallTime = DateTime.UtcNow;
            return SendMessage(opName, requestXml);
        }
        catch (CommunicationException)
        {
            // Channel may be faulted — recreate and retry once
            RecreateChannel();
            return SendMessage(opName, requestXml);
        }
        finally
        {
            channelSem.Release();
        }
    }

    public string GetCurrentToken()
    {
        lock (tokenLock) { return accessToken; }
    }

    // All SOAP calls go through this method. Caller must hold channelSem.
    string SendMessage(string opName, string requestXml)
    {
        string bodyXml = "<" + opName + " xmlns=\"http://tempuri.org/\">" +
                         requestXml + "</" + opName + ">";
        var reader = XmlReader.Create(new StringReader(bodyXml));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/" + opName,
            reader);
        Message result = channel.ProcessMessage(msg);

        using (var sw = new StringWriter())
        using (var writer = XmlWriter.Create(sw, new XmlWriterSettings { Indent = false }))
        {
            result.WriteBody(writer);
            writer.Flush();
            return sw.ToString();
        }
    }

    string BuildGetTokenXml()
    {
        return "<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
            "<AccessToken i:nil=\"true\" xmlns=\"\"/>" +
            "<ClientId xmlns=\"\">" + clientId + "</ClientId>" +
            "<CompanyInitials xmlns=\"\">" + clientId + "</CompanyInitials>" +
            "<IsDeveloper xmlns=\"\">false</IsDeveloper>" +
            "<RequestId xmlns=\"\">" + Guid.NewGuid() + "</RequestId>" +
            "<RequestedByUserName i:nil=\"true\" xmlns=\"\"/>" +
            "<Version i:nil=\"true\" xmlns=\"\"/>" +
            "</request>";
    }

    static string ExtractXmlValue(string xml, string tag)
    {
        int start = xml.IndexOf("<" + tag);
        if (start < 0) return null;
        int tagEnd = xml.IndexOf(">", start);
        string tagStr = xml.Substring(start, tagEnd - start + 1);
        if (tagStr.Contains("nil=\"true\"")) return null;
        start = tagEnd + 1;
        int end = xml.IndexOf("</" + tag + ">", start);
        if (end < 0) return null;
        return xml.Substring(start, end - start);
    }
}
```

**Step 2: Wire SoapBridge into Main, replace the /api/soap stub**

In `HandleRequest`, replace the 501 stub with:

```csharp
// In /api/soap/ handler:
string requestBody = new StreamReader(ctx.Request.InputStream).ReadToEnd();
string token = bridge.GetCurrentToken();
string cid = bridge.ClientId;
string requestXml = JsonToXml(opName, requestBody, token, cid); // Task A4
string responseXml = bridge.CallSoap(opName, requestXml);
string responseJson = XmlToJson(responseXml); // Task A5
// Check for SOAP fault in response and map to HTTP status
int httpStatus = 200;
if (responseJson.Contains("\"error\":\"unisoft_fault\""))
    httpStatus = 502;
else if (responseJson.Contains("\"error\":\"unisoft_validation\""))
    httpStatus = 422;
WriteJson(ctx, httpStatus, responseJson);
```

Also add `public string ClientId { get { return clientId; } }` to the `SoapBridge` class.

For this task, use a **passthrough stub** for `JsonToXml` that builds the standard request with any JSON keys as flat XML fields (works for Get* operations). The stub signature must match the final: `static string JsonToXml(string opName, string json, string token, string clientId)`. `XmlToJson` returns the raw XML wrapped in JSON. Both are replaced with proper translation in Tasks A4 and A5.

**Step 3: Deploy and test**

From Mac, test with the health endpoint and a real SOAP call:

```bash
curl http://<EC2_IP>:5000/api/health
# Should show token info

curl -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceLOBs \
  -H "X-Api-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{}'
# Should return XML or JSON with 18 LOBs
```

**Step 4: Commit**

```bash
git commit -m "feat(unisoft-proxy): SOAP bridge with WCF channel, token management, keepalive"
```

---

### Task A4: JSON → XML translation (inbound)

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Implement JsonToXml with DTO namespace registry**

Add the DTO namespace registry and the JSON→XML converter. The converter:
1. Parses JSON manually (simple recursive parser — no JSON.NET available without NuGet)
2. For each key-value pair, checks the DTO namespace registry
3. If key is a known DTO, wraps children in namespaced elements with `b:` prefix
4. Otherwise, emits as flat `xmlns=""` element
5. Injects RequestBase fields (AccessToken, ClientId, etc.)

**Implementation note:** .NET Framework 4.8 has `System.Web.Extensions` with `JavaScriptSerializer` in the GAC. Use this for JSON parsing. Add `/reference:System.Web.Extensions.dll` to the compile command.

```csharp
using System.Web.Script.Serialization;
using System.Collections.Generic;

// DTO Namespace Registry
static Dictionary<string, string> dtoNamespaces = new Dictionary<string, string>
{
    {"Quote", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes"},
    {"QuoteActivity", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes"},
    {"QuoteStatus", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes"},
    {"Submission", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes.Submissions"},
    {"Activity", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Activities"},
    {"CashDetail", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Cash"},
    {"PolicyEntry", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.PolicyInquiry"},
};

// RequestBase fields the proxy injects (caller must NOT send these)
static HashSet<string> requestBaseFields = new HashSet<string>
{
    "AccessToken", "ClientId", "CompanyInitials", "IsDeveloper",
    "RequestId", "RequestedByUserName", "Version"
};

static string JsonToXml(string opName, string json, string token, string clientId)
{
    var serializer = new JavaScriptSerializer();
    serializer.MaxJsonLength = 5 * 1024 * 1024;
    var dict = string.IsNullOrWhiteSpace(json) || json.Trim() == "{}"
        ? new Dictionary<string, object>()
        : serializer.Deserialize<Dictionary<string, object>>(json);

    var sb = new StringBuilder();
    sb.Append("<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">");

    // Inject RequestBase
    sb.Append("<AccessToken xmlns=\"\">" + Escape(token) + "</AccessToken>");
    sb.Append("<ClientId xmlns=\"\">" + Escape(clientId) + "</ClientId>");
    sb.Append("<CompanyInitials xmlns=\"\">" + Escape(clientId) + "</CompanyInitials>");
    sb.Append("<IsDeveloper xmlns=\"\">false</IsDeveloper>");
    sb.Append("<RequestId xmlns=\"\">" + Guid.NewGuid() + "</RequestId>");
    sb.Append("<RequestedByUserName i:nil=\"true\" xmlns=\"\"/>");
    sb.Append("<Version i:nil=\"true\" xmlns=\"\"/>");

    // Caller fields
    foreach (var kvp in dict)
    {
        if (requestBaseFields.Contains(kvp.Key)) continue; // skip — proxy controls these
        AppendField(sb, kvp.Key, kvp.Value);
    }

    sb.Append("</request>");
    return sb.ToString();
}

static void AppendField(StringBuilder sb, string key, object value)
{
    if (value == null)
    {
        string ns;
        if (dtoNamespaces.TryGetValue(key, out ns))
            sb.Append("<" + key + " i:nil=\"true\" xmlns=\"\" xmlns:b=\"" + ns + "\"/>");
        else
            sb.Append("<" + key + " i:nil=\"true\" xmlns=\"\"/>");
        return;
    }

    string dtoNs;
    if (dtoNamespaces.TryGetValue(key, out dtoNs) && value is Dictionary<string, object>)
    {
        // Nested DTO with namespace
        var dict = (Dictionary<string, object>)value;
        sb.Append("<" + key + " xmlns=\"\" xmlns:b=\"" + dtoNs + "\">");
        foreach (var kvp in dict)
        {
            AppendDtoField(sb, kvp.Key, kvp.Value);
        }
        sb.Append("</" + key + ">");
    }
    else
    {
        // Flat field
        sb.Append("<" + key + " xmlns=\"\">" + Escape(value.ToString()) + "</" + key + ">");
    }
}

static void AppendDtoField(StringBuilder sb, string key, object value)
{
    if (value == null)
    {
        sb.Append("<b:" + key + " i:nil=\"true\"/>");
        return;
    }
    if (value is Dictionary<string, object>)
    {
        // Sub-DTO — emit as nil (design says sub-DTOs are null in write requests)
        sb.Append("<b:" + key + " i:nil=\"true\"/>");
        return;
    }
    sb.Append("<b:" + key + ">" + Escape(value.ToString()) + "</b:" + key + ">");
}

static string Escape(string s)
{
    return s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;").Replace("\"", "&quot;");
}
```

**Step 2: Update compile command to include System.Web.Extensions.dll**

In the compile script, add `/reference:System.Web.Extensions.dll` to the csc.exe command.

**Step 3: Deploy and test with a read operation (flat JSON)**

```bash
curl -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceLOBs \
  -H "X-Api-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected: 18 LOBs returned.

```bash
curl -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceSubLOBs \
  -H "X-Api-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{"LOB": "CG"}'
```

Expected: 4 sub-LOBs (AC, LL, HM, SE).

**Step 4: Commit**

```bash
git commit -m "feat(unisoft-proxy): JSON→XML translation with DTO namespace registry"
```

---

### Task A5: XML → JSON translation (outbound)

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Implement XmlToJson**

Converts the SOAP response XML body to JSON. Handles:
- ResponseBase fields → `_meta` object
- Namespace prefix stripping (`b:LOB` → `LOB`)
- `*DTO` child pattern → always JSON array
- `i:nil="true"` → `null`
- Nested elements → nested JSON objects

```csharp
static HashSet<string> metaFields = new HashSet<string>
{
    "Build", "CorrelationId", "Message", "ReplyStatus", "RowsAffected", "Version"
};

static string XmlToJson(string xml)
{
    // Parse XML
    var doc = new XmlDocument();
    doc.LoadXml(xml);

    // WriteBody output starts at the SOAP body content.
    // Structure is either:
    //   <s:Body><XXXResponse><XXXResult>...data...</XXXResult></XXXResponse></s:Body>
    //   <s:Body><s:Fault>...</s:Fault></s:Body>
    //
    // WriteBody gives us everything inside <s:Body>, so root is either:
    //   - The Body element itself (containing Response or Fault children)
    //   - The Response element directly (if WriteBody unwraps Body)
    //
    // We handle both cases by searching downward for the Result element.
    XmlNode root = doc.DocumentElement;
    XmlNode resultNode = null;

    // Check if root IS the Response element (WriteBody typically gives us this)
    if (root.LocalName.EndsWith("Response"))
    {
        // Look for the Result child directly
        foreach (XmlNode child in root.ChildNodes)
        {
            if (child.LocalName.EndsWith("Result"))
            {
                resultNode = child;
                break;
            }
        }
        if (resultNode == null) resultNode = root;
    }
    else if (root.LocalName == "Body")
    {
        // Root is the Body element — look for Response > Result
        foreach (XmlNode child in root.ChildNodes)
        {
            if (child.LocalName == "Fault")
                return BuildFaultJson(child);
            if (child.LocalName.EndsWith("Response"))
            {
                foreach (XmlNode grandchild in child.ChildNodes)
                {
                    if (grandchild.LocalName.EndsWith("Result"))
                    {
                        resultNode = grandchild;
                        break;
                    }
                }
                if (resultNode == null) resultNode = child;
                break;
            }
        }
    }
    else if (root.LocalName == "Fault")
    {
        return BuildFaultJson(root);
    }

    if (resultNode == null) resultNode = root;

    // Separate meta from data
    var meta = new StringBuilder();
    var data = new StringBuilder();
    meta.Append("\"_meta\":{");
    bool firstMeta = true;
    bool firstData = true;

    foreach (XmlNode child in resultNode.ChildNodes)
    {
        string localName = child.LocalName;
        if (metaFields.Contains(localName))
        {
            if (!firstMeta) meta.Append(",");
            meta.Append("\"" + localName + "\":" + NodeToJsonValue(child));
            firstMeta = false;
        }
        else
        {
            if (!firstData) data.Append(",");
            data.Append("\"" + StripPrefix(localName) + "\":" + NodeToJsonValue(child));
            firstData = false;
        }
    }
    meta.Append("}");

    return "{" + meta + (firstData ? "" : "," + data) + "}";
}

static string NodeToJsonValue(XmlNode node)
{
    // Check nil
    if (node.Attributes != null)
    {
        foreach (XmlAttribute attr in node.Attributes)
        {
            if (attr.LocalName == "nil" && attr.Value == "true")
                return "null";
        }
    }

    // Leaf node (text content only)
    if (!node.HasChildNodes || (node.ChildNodes.Count == 1 && node.FirstChild.NodeType == XmlNodeType.Text))
    {
        string text = node.InnerText;
        // Try number
        int intVal;
        decimal decVal;
        if (int.TryParse(text, out intVal)) return intVal.ToString();
        if (decimal.TryParse(text, out decVal) && text.Contains(".")) return decVal.ToString();
        if (text == "true" || text == "false") return text;
        return "\"" + JsonEscape(text) + "\"";
    }

    // Check if children are a DTO array (repeated elements with *DTO names)
    var childNames = new Dictionary<string, int>();
    foreach (XmlNode child in node.ChildNodes)
    {
        if (child.NodeType != XmlNodeType.Element) continue;
        string ln = child.LocalName;
        if (childNames.ContainsKey(ln)) childNames[ln]++;
        else childNames[ln] = 1;
    }

    // If single child type ending in DTO, or multiple children with same name → array
    if (childNames.Count == 1)
    {
        string childName = null;
        int count = 0;
        foreach (var kvp in childNames) { childName = kvp.Key; count = kvp.Value; }
        if (childName.EndsWith("DTO") || count > 1)
        {
            var arr = new StringBuilder("[");
            bool first = true;
            foreach (XmlNode child in node.ChildNodes)
            {
                if (child.NodeType != XmlNodeType.Element) continue;
                if (!first) arr.Append(",");
                arr.Append(ElementToJsonObject(child));
                first = false;
            }
            arr.Append("]");
            return arr.ToString();
        }
    }

    // Object
    return ElementToJsonObject(node);
}

static string ElementToJsonObject(XmlNode node)
{
    // Check nil
    if (node.Attributes != null)
        foreach (XmlAttribute attr in node.Attributes)
            if (attr.LocalName == "nil" && attr.Value == "true")
                return "null";

    var sb = new StringBuilder("{");
    bool first = true;
    foreach (XmlNode child in node.ChildNodes)
    {
        if (child.NodeType != XmlNodeType.Element) continue;
        if (!first) sb.Append(",");
        sb.Append("\"" + StripPrefix(child.LocalName) + "\":" + NodeToJsonValue(child));
        first = false;
    }
    sb.Append("}");
    return sb.ToString();
}

static string StripPrefix(string name)
{
    int colon = name.IndexOf(':');
    return colon >= 0 ? name.Substring(colon + 1) : name;
}

static string JsonEscape(string s)
{
    return s.Replace("\\", "\\\\").Replace("\"", "\\\"")
            .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
}

static string BuildFaultJson(XmlNode faultNode)
{
    string reason = "";
    string code = "";
    foreach (XmlNode child in faultNode.ChildNodes)
    {
        if (child.LocalName == "Reason")
            reason = child.InnerText;
        if (child.LocalName == "Code")
            code = child.InnerText;
    }
    return "{\"_meta\":{\"ReplyStatus\":\"Fault\"},\"error\":\"unisoft_fault\"," +
           "\"message\":\"" + JsonEscape(reason) + "\",\"faultCode\":\"" + JsonEscape(code) + "\"}";
}
```

**Step 2: Deploy and test**

```bash
# Test read with proper JSON output
curl -s -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceLOBs \
  -H "X-Api-Key: dev-key" -H "Content-Type: application/json" -d '{}' | python3 -m json.tool

# Test with parameters
curl -s -X POST http://<EC2_IP>:5000/api/soap/GetCarriersForLookup \
  -H "X-Api-Key: dev-key" -H "Content-Type: application/json" -d '{}' | python3 -m json.tool

# Test with sub-LOBs
curl -s -X POST http://<EC2_IP>:5000/api/soap/GetInsuranceSubLOBs \
  -H "X-Api-Key: dev-key" -H "Content-Type: application/json" -d '{"LOB":"CG"}' | python3 -m json.tool
```

Expected: Clean JSON with `_meta` and data fields. Arrays for DTO collections.

**Step 3: Commit**

```bash
git commit -m "feat(unisoft-proxy): XML→JSON translation with meta separation, array detection, namespace stripping"
```

---

### Task A6: Structured logging

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Add Logger class**

```csharp
class Logger
{
    static string logDir = "C:\\unisoft\\logs";
    static object fileLock = new object();

    public static void Log(string op, int statusCode, long durationMs, string detail = null)
    {
        string ts = DateTime.UtcNow.ToString("o");
        string line = "{\"ts\":\"" + ts + "\",\"op\":\"" + JsonEscape(op ?? "") +
            "\",\"status\":" + statusCode + ",\"duration_ms\":" + durationMs +
            (detail != null ? ",\"detail\":\"" + JsonEscape(detail) + "\"" : "") + "}";

        Console.WriteLine(line);

        lock (fileLock)
        {
            string file = Path.Combine(logDir, "proxy-" + DateTime.UtcNow.ToString("yyyy-MM-dd") + ".log");
            Directory.CreateDirectory(logDir);
            File.AppendAllText(file, line + "\n");
        }
    }

    public static void Info(string message)
    {
        Log(null, 0, 0, message);
    }
}
```

**Step 2: Wire logging into HandleRequest**

Add `Stopwatch` timing around each SOAP call. Log operation name, HTTP status, duration, and any errors. Ensure `using System.Diagnostics;` is at the top of the file (already added in Task A2).

**Step 3: Add log cleanup** (delete files older than 30 days on startup)

**Step 4: Deploy, make a few calls, verify log file on EC2**

```bash
# Check log via SSM
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["Get-Content C:\\unisoft\\logs\\proxy-2026-04-01.log -Tail 10"]}'
```

**Step 5: Commit**

```bash
git commit -m "feat(unisoft-proxy): structured JSON logging with daily rotation"
```

---

### Task A7: Windows Service wrapper

**Files:**
- Modify: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

**Step 1: Add ServiceBase wrapper**

Wrap the existing `Main` logic so the exe can run both as a console app (for testing) and as a Windows Service:

```csharp
using System.ServiceProcess;

class UniProxyService : ServiceBase
{
    Thread listenerThread;

    public UniProxyService()
    {
        ServiceName = "UniProxy";
    }

    protected override void OnStart(string[] args)
    {
        listenerThread = new Thread(() => UniProxy.Run());
        listenerThread.IsBackground = true;
        listenerThread.Start();
    }

    protected override void OnStop()
    {
        // HttpListener.Stop() + channel cleanup
        UniProxy.Shutdown();
    }
}

// In Main:
static void Main(string[] args)
{
    if (args.Length > 0 && args[0] == "--console")
    {
        Run();
    }
    else if (Environment.UserInteractive)
    {
        Run(); // dev mode
    }
    else
    {
        ServiceBase.Run(new UniProxyService());
    }
}
```

**Step 2: Add `/reference:System.ServiceProcess.dll` to compile command**

**Step 3: Deploy, test console mode (`UniProxy.exe --console`), then register as service**

```powershell
# On EC2 via SSM:
sc create UniProxy binPath= "C:\unisoft\UniProxy.exe" start= auto
sc failure UniProxy reset= 86400 actions= restart/5000/restart/10000/restart/30000
netsh http add urlacl url=http://+:5000/ user="NT AUTHORITY\SYSTEM"
sc start UniProxy
sc query UniProxy
```

**Step 4: Verify the service is running**

```bash
curl http://<EC2_IP>:5000/api/health
```

**Step 5: Commit**

```bash
git commit -m "feat(unisoft-proxy): Windows Service wrapper with console fallback"
```

---

## Track B: Infrastructure

All tasks use AWS CLI from Mac. No code changes.

### Task B1: Downsize EC2 to t3.small

**Step 1: Stop instance (if running)**
```bash
aws ec2 stop-instances --instance-ids i-0dc2563c9bc92aa0e
aws ec2 wait instance-stopped --instance-ids i-0dc2563c9bc92aa0e
```

**Step 2: Change instance type**
```bash
aws ec2 modify-instance-attribute --instance-ids i-0dc2563c9bc92aa0e --instance-type t3.small
```

**Step 3: Start and verify**
```bash
aws ec2 start-instances --instance-ids i-0dc2563c9bc92aa0e
aws ec2 wait instance-running --instance-ids i-0dc2563c9bc92aa0e
aws ec2 describe-instances --instance-ids i-0dc2563c9bc92aa0e \
  --query 'Reservations[0].Instances[0].[InstanceType,State.Name]' --output text
```

Expected: `t3.small running`

---

### Task B2: Allocate Elastic IP

**Step 1: Allocate**
```bash
aws ec2 allocate-address --domain vpc --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=unisoft-proxy}]'
# Note the AllocationId from output
```

**Step 2: Associate**
```bash
aws ec2 associate-address --instance-id i-0dc2563c9bc92aa0e --allocation-id <eipalloc-xxx>
```

**Step 3: Verify**
```bash
aws ec2 describe-addresses --allocation-ids <eipalloc-xxx> --query 'Addresses[0].PublicIp' --output text
```

Record the Elastic IP — this is the proxy's stable address.

---

### Task B3: Configure security group

**Step 1: Find the instance's security group**
```bash
aws ec2 describe-instances --instance-ids i-0dc2563c9bc92aa0e \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text
```

**Step 2: Open port 5000 for Railway and dev**
```bash
SG_ID=<sg-xxx>

# Railway static IP
aws ec2 authorize-security-group-ingress --group-id $SG_ID \
  --protocol tcp --port 5000 --cidr 162.220.234.15/32

# Craig's current IP (look up with: curl ifconfig.me)
aws ec2 authorize-security-group-ingress --group-id $SG_ID \
  --protocol tcp --port 5000 --cidr <your-ip>/32
```

**Step 3: Verify**
```bash
aws ec2 describe-security-groups --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5000`]'
```

---

### Task B4: Set environment variables on EC2

**Step 1: Set env vars via SSM** (persist in system environment)

```bash
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":[
    "[Environment]::SetEnvironmentVariable(\"UNISOFT_SOAP_URL\", \"https://services.uat.gicunderwriters.co/management/imsservice.svc\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"UNISOFT_WS_USER\", \"UniClient\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"UNISOFT_WS_PASS\", \"<get from research/unisoft-api-reference.md SOAP Auth section>\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"UNISOFT_CLIENT_ID\", \"GIC_UAT\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"UNISOFT_SKIP_CERT_VALIDATION\", \"true\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"PROXY_API_KEY\", \"<generate-a-key>\", \"Machine\")",
    "[Environment]::SetEnvironmentVariable(\"PROXY_PORT\", \"5000\", \"Machine\")",
    "Write-Output \"Environment variables set\""
  ]}'
```

**Step 2: Verify**

```bash
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["[Environment]::GetEnvironmentVariable(\"PROXY_PORT\", \"Machine\")"]}'
```

---

### Task B5: URL ACL + directory setup

```bash
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":[
    "netsh http add urlacl url=http://+:5000/ user=\"NT AUTHORITY\\SYSTEM\"",
    "New-Item -ItemType Directory -Path C:\\unisoft\\logs -Force",
    "Write-Output \"URL ACL and directories ready\""
  ]}'
```

---

## Track C: Python Client + Integration Tests

This track produces a Python client library and test suite. Code can be written immediately; integration tests run after Tracks A+B complete.

### Task C1: Python client library

**Files:**
- Create: `projects/gic-email-intelligence/unisoft-proxy/client/unisoft_client.py`

A thin Python wrapper:

```python
"""Unisoft REST Proxy client."""
import requests
from typing import Any

class UnisoftClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def call(self, operation: str, params: dict | None = None) -> dict:
        """Call any Unisoft SOAP operation via the proxy."""
        resp = requests.post(
            f"{self.base_url}/api/soap/{operation}",
            json=params or {},
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        data = resp.json()
        if resp.status_code >= 400:
            raise UnisoftError(resp.status_code, data)
        return data

    def health(self) -> dict:
        resp = requests.get(f"{self.base_url}/api/health", timeout=10)
        return resp.json()

    # Convenience methods for common operations
    def get_lobs(self) -> list:
        return self.call("GetInsuranceLOBs").get("InsuranceLOBs", [])

    def get_sub_lobs(self, lob: str) -> list:
        return self.call("GetInsuranceSubLOBs", {"LOB": lob}).get("InsuranceSubLOBs", [])

    def get_carriers(self) -> list:
        return self.call("GetCarriersForLookup").get("CarriersForLookup", [])

    def get_agents(self) -> list:
        return self.call("GetAgentsAndProspectsForLookup").get("AgentsMinimal", [])

    def create_quote(self, quote_data: dict, action: str = "Insert") -> dict:
        return self.call("SetQuote", {"Action": action, "IsNewSystem": True, "Quote": quote_data})

    def create_submission(self, submission_data: dict) -> dict:
        return self.call("SetSubmission", {"Submission": submission_data})

    def create_activity(self, activity_data: dict, action: str = "Insert") -> dict:
        return self.call("SetActivity", {"Action": action, "Activity": activity_data})

    def get_quote(self, quote_id: int) -> dict:
        return self.call("GetQuote", {"QuoteId": quote_id})

    def get_submissions(self, quote_id: int) -> dict:
        return self.call("GetSubmissions", {"QuoteId": quote_id})

class UnisoftError(Exception):
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self.data = data
        super().__init__(f"Unisoft API error {status_code}: {data}")
```

**Commit:**
```bash
git commit -m "feat(unisoft-proxy): Python client library"
```

---

### Task C2: Integration test suite

**Files:**
- Create: `projects/gic-email-intelligence/unisoft-proxy/client/test_integration.py`

**Requires:** Proxy running (Tracks A+B complete). Set `UNISOFT_PROXY_URL` and `UNISOFT_PROXY_KEY` env vars.

```python
"""Integration tests for the Unisoft REST proxy."""
import os
import sys
from unisoft_client import UnisoftClient, UnisoftError

PROXY_URL = os.environ.get("UNISOFT_PROXY_URL", "http://localhost:5000")
API_KEY = os.environ.get("UNISOFT_PROXY_KEY", "dev-key")

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print("  PASS: " + name)
        passed += 1
    except Exception as e:
        print("  FAIL: " + name + " -- " + str(e))
        failed += 1

def test_health():
    h = client.health()
    if h["status"] != "ok":
        raise Exception("Expected status 'ok', got " + h["status"])

def test_lobs():
    lobs = client.get_lobs()
    if len(lobs) != 18:
        raise Exception("Expected 18 LOBs, got " + str(len(lobs)))

def test_sub_lobs():
    subs = client.get_sub_lobs("CG")
    if len(subs) != 4:
        raise Exception("Expected 4 sub-LOBs, got " + str(len(subs)))

def test_carriers():
    carriers = client.get_carriers()
    if len(carriers) != 46:
        raise Exception("Expected 46 carriers, got " + str(len(carriers)))

def test_agents():
    agents = client.get_agents()
    if len(agents) < 3000:
        raise Exception("Expected 3000+ agents, got " + str(len(agents)))

def test_quote_actions():
    result = client.call("GetQuoteActions")
    if "_meta" not in result:
        raise Exception("Missing _meta in response")
    if result["_meta"]["ReplyStatus"] != "Success":
        raise Exception("ReplyStatus is not Success")

def test_auth_failure():
    bad_client = UnisoftClient(PROXY_URL, "wrong-key")
    try:
        bad_client.call("GetInsuranceLOBs")
        raise Exception("Expected UnisoftError for bad API key")
    except UnisoftError as e:
        if e.status_code != 401:
            raise Exception("Expected 401, got " + str(e.status_code))

if __name__ == "__main__":
    client = UnisoftClient(PROXY_URL, API_KEY)
    print("=== Unisoft Proxy Integration Tests ===")
    print("URL: " + PROXY_URL + "\n")

    test("Health check", test_health)
    test("GetInsuranceLOBs returns 18", test_lobs)
    test("GetInsuranceSubLOBs CG returns 4", test_sub_lobs)
    test("GetCarriersForLookup returns 46", test_carriers)
    test("GetAgentsAndProspectsForLookup returns 3000+", test_agents)
    test("GetQuoteActions returns actions", test_quote_actions)
    test("Invalid API key returns 401", test_auth_failure)

    print("\n=== Results: " + str(passed) + " passed, " + str(failed) + " failed ===")
    sys.exit(0 if failed == 0 else 1)
```

**Run:**
```bash
UNISOFT_PROXY_URL=http://<elastic-ip>:5000 UNISOFT_PROXY_KEY=<key> python3 test_integration.py
```

**Commit:**
```bash
git commit -m "feat(unisoft-proxy): integration test suite"
```

---

## Execution Order for Orchestrator

```
┌─────────────────────┐  ┌─────────────────────┐
│   Session 1          │  │   Session 2          │
│   Track A: Code      │  │   Track B: Infra     │
│                      │  │                      │
│   A1: Scaffold       │  │   B1: Downsize EC2   │
│   A2: HTTP listener  │  │   B2: Elastic IP     │
│   A3: SOAP bridge    │  │   B3: Security group │
│   A4: JSON→XML       │  │   B4: Env vars       │
│   A5: XML→JSON       │  │   B5: URL ACL        │
│   A6: Logging        │  │                      │
│   A7: Service wrapper│  │   Track C: Client    │
│                      │  │   C1: Python client  │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           └────────────┬────────────┘
                        │
              ┌─────────▼──────────┐
              │   Orchestrator     │
              │   C2: Integration  │
              │   tests            │
              └────────────────────┘
```

**Session 1** does all of Track A (sequential, each task builds on prior).
**Session 2** does Track B (fast, ~15 min), then starts Track C1 (Python client).
**Orchestrator** runs C2 integration tests after both sessions complete.

**Note on Track A testing:** Tasks A2-A5 need the EC2 running to test. Session 1 can start writing code immediately (A1) but needs Track B1 (EC2 start/downsize) complete before testing. The orchestrator should ensure B1 completes early so Session 1 isn't blocked.
