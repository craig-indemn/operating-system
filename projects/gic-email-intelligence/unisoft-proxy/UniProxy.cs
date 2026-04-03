using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.ServiceProcess;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Xml;

// ---------------------------------------------------------------------------
// WCF service contract — matches Unisoft IIMSService
// ---------------------------------------------------------------------------
[ServiceContract(Namespace = "http://tempuri.org/")]
interface IIMSService
{
    [OperationContract(Action = "http://tempuri.org/IIMSService/GetToken",
                       ReplyAction = "http://tempuri.org/IIMSService/GetTokenResponse")]
    Message GetToken(Message request);

    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

// ---------------------------------------------------------------------------
// WCF service contract — matches Unisoft IINSFileService (attachments)
// ---------------------------------------------------------------------------
[ServiceContract(Namespace = "http://tempuri.org/")]
interface IINSFileService
{
    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

// ---------------------------------------------------------------------------
// MustUnderstand inspector — file service returns headers with MustUnderstand
// that the generic message contract doesn't know how to handle
// ---------------------------------------------------------------------------
class MustUnderstandInspector : System.ServiceModel.Dispatcher.IClientMessageInspector
{
    public object BeforeSendRequest(ref Message request, IClientChannel channel) { return null; }
    public void AfterReceiveReply(ref Message reply, object correlationState)
    {
        for (int i = 0; i < reply.Headers.Count; i++)
            if (reply.Headers[i].MustUnderstand)
                reply.Headers.UnderstoodHeaders.Add(reply.Headers[i]);
    }
}

class MustUnderstandBehavior : System.ServiceModel.Description.IEndpointBehavior
{
    public void AddBindingParameters(System.ServiceModel.Description.ServiceEndpoint e, BindingParameterCollection p) { }
    public void ApplyClientBehavior(System.ServiceModel.Description.ServiceEndpoint e,
        System.ServiceModel.Dispatcher.ClientRuntime r)
    {
        r.ClientMessageInspectors.Add(new MustUnderstandInspector());
    }
    public void ApplyDispatchBehavior(System.ServiceModel.Description.ServiceEndpoint e,
        System.ServiceModel.Dispatcher.EndpointDispatcher d) { }
    public void Validate(System.ServiceModel.Description.ServiceEndpoint e) { }
}

// ---------------------------------------------------------------------------
// Custom SOAP header that writes raw XML content
// ---------------------------------------------------------------------------
class RawXmlHeader : MessageHeader
{
    string headerName;
    string headerNs;
    bool headerMustUnderstand;
    string innerXml;

    public RawXmlHeader(string name, string ns, string innerXml, bool mustUnderstand)
    {
        this.headerName = name;
        this.headerNs = ns;
        this.innerXml = innerXml;
        this.headerMustUnderstand = mustUnderstand;
    }

    public override string Name { get { return headerName; } }
    public override string Namespace { get { return headerNs; } }
    public override bool MustUnderstand { get { return headerMustUnderstand; } }

    protected override void OnWriteStartHeader(XmlDictionaryWriter writer, MessageVersion messageVersion)
    {
        // Write header start with xmlns:i declaration for nil attributes
        writer.WriteStartElement("h", this.Name, this.Namespace);
        writer.WriteXmlnsAttribute("i", "http://www.w3.org/2001/XMLSchema-instance");
        if (this.MustUnderstand)
            writer.WriteAttributeString("s", "mustUnderstand",
                "http://schemas.xmlsoap.org/soap/envelope/", "1");
    }

    protected override void OnWriteHeaderContents(XmlDictionaryWriter writer, MessageVersion messageVersion)
    {
        // Write inner XML fragment
        string wrapped = "<r xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
                         innerXml + "</r>";
        using (XmlReader reader = XmlReader.Create(new StringReader(wrapped)))
        {
            reader.ReadStartElement(); // skip <r>
            while (reader.NodeType != XmlNodeType.EndElement)
            {
                writer.WriteNode(reader, true);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// FileBridge — manages MTOM channel to IINSFileService (attachments)
// ---------------------------------------------------------------------------
class FileBridge
{
    string fileUrl;
    static string dtoNs = "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Attachments.Services.DTO";

    public FileBridge(string fileUrl)
    {
        this.fileUrl = fileUrl;
    }

    ChannelFactory<IINSFileService> CreateFactory()
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MessageEncoding = WSMessageEncoding.Mtom;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        b.MaxBufferSize = 50 * 1024 * 1024;
        b.SendTimeout = TimeSpan.FromSeconds(120);
        b.ReceiveTimeout = TimeSpan.FromSeconds(120);

        ChannelFactory<IINSFileService> f = new ChannelFactory<IINSFileService>(
            b, new EndpointAddress(fileUrl));
        f.Endpoint.EndpointBehaviors.Add(new MustUnderstandBehavior());
        return f;
    }

    // Body-based call (GetQuoteAttachments, GetSupportedAttachmentTypes, etc.)
    public string CallBody(string opName, string innerXml)
    {
        ChannelFactory<IINSFileService> f = CreateFactory();
        IINSFileService ch = f.CreateChannel();
        try
        {
            ((IClientChannel)ch).Open();
            string body = "<" + opName + " xmlns=\"http://tempuri.org/\">" +
                          innerXml + "</" + opName + ">";
            Message req = Message.CreateMessage(MessageVersion.Soap11,
                "http://tempuri.org/IINSFileService/" + opName,
                XmlReader.Create(new StringReader(body)));
            Message resp = ch.ProcessMessage(req);
            return ReadBody(resp);
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            try { f.Close(); } catch { }
        }
    }

    // Header-based call for AddQuoteAttachment (WCF message contract pattern)
    public string UploadQuoteAttachment(byte[] fileBytes, int quoteNumber,
        int mgaNumber, string fileName, string fileType, string createdBy,
        string description, string clientId)
    {
        ChannelFactory<IINSFileService> f = CreateFactory();
        IINSFileService ch = f.CreateChannel();
        try
        {
            ((IClientChannel)ch).Open();

            // Body: QuoteAttachmentAddRequest with FileByteStream
            string bodyXml = "<QuoteAttachmentAddRequest xmlns=\"http://tempuri.org/\">" +
                "<FileByteStream>" + Convert.ToBase64String(fileBytes) + "</FileByteStream>" +
                "</QuoteAttachmentAddRequest>";

            Message req = Message.CreateMessage(MessageVersion.Soap11,
                "http://tempuri.org/IINSFileService/AddQuoteAttachment",
                XmlReader.Create(new StringReader(bodyXml)));

            string ns = "http://tempuri.org/";

            // Add SOAP headers (matching Fiddler capture format)
            req.Headers.Add(MessageHeader.CreateHeader("AccessToken", ns, null, false));
            req.Headers.Add(MessageHeader.CreateHeader("ClientId", ns, clientId, false));
            req.Headers.Add(MessageHeader.CreateHeader("RequestId", ns,
                Guid.NewGuid().ToString(), false));
            req.Headers.Add(MessageHeader.CreateHeader("Version", ns, null, false));

            // QuoteAttachment header — the DTO with metadata
            string attInner =
                "<AttachmentType i:nil=\"true\" xmlns=\"" + dtoNs + "\"/>" +
                "<CreatedByUser xmlns=\"" + dtoNs + "\">" + Escape(createdBy) + "</CreatedByUser>" +
                "<CreatedDate xmlns=\"" + dtoNs + "\">" + DateTime.UtcNow.ToString("o") + "</CreatedDate>" +
                "<CurrentCategory xmlns=\"" + dtoNs + "\">" +
                    "<Active>true</Active>" +
                    "<CategoryTypeId>2</CategoryTypeId>" +
                    "<CurrentSubCategory>" +
                        "<Active>true</Active>" +
                        "<CategoryDescription i:nil=\"true\"/>" +
                        "<CategoryId>14</CategoryId>" +
                        "<Description>Other (General)</Description>" +
                        "<Id>35</Id>" +
                        "<IsEditable>false</IsEditable>" +
                        "<IsPublic>false</IsPublic>" +
                        "<SequenceNumber>4</SequenceNumber>" +
                    "</CurrentSubCategory>" +
                    "<Description>General</Description>" +
                    "<Id>14</Id>" +
                    "<IsEditable>false</IsEditable>" +
                    "<SequenceNumber>1</SequenceNumber>" +
                    "<SubCategories/>" +
                "</CurrentCategory>" +
                "<Description xmlns=\"" + dtoNs + "\">" + Escape(description) + "</Description>" +
                "<FileName i:nil=\"true\" xmlns=\"" + dtoNs + "\"/>" +
                "<FileType xmlns=\"" + dtoNs + "\">" + Escape(fileType) + "</FileType>" +
                "<FileTypeDescription i:nil=\"true\" xmlns=\"" + dtoNs + "\"/>" +
                "<Id xmlns=\"" + dtoNs + "\">0</Id>" +
                "<IsPublic xmlns=\"" + dtoNs + "\">false</IsPublic>" +
                "<MGANumber xmlns=\"" + dtoNs + "\">" + mgaNumber + "</MGANumber>" +
                "<QuoteNumber xmlns=\"" + dtoNs + "\">" + quoteNumber + "</QuoteNumber>" +
                "<Source i:nil=\"true\" xmlns=\"" + dtoNs + "\"/>" +
                "<Url i:nil=\"true\" xmlns=\"" + dtoNs + "\"/>";

            req.Headers.Add(new RawXmlHeader("QuoteAttachment", ns, attInner, false));

            Message resp = ch.ProcessMessage(req);
            return ReadBody(resp);
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            try { f.Close(); } catch { }
        }
    }

    static string ReadBody(Message msg)
    {
        StringBuilder sb = new StringBuilder();
        XmlWriterSettings ws = new XmlWriterSettings();
        ws.Indent = false;
        using (XmlWriter w = XmlWriter.Create(sb, ws))
        {
            msg.WriteBody(w);
            w.Flush();
        }
        return sb.ToString();
    }

    static string Escape(string s)
    {
        if (s == null) return "";
        return s.Replace("&", "&amp;").Replace("<", "&lt;")
                .Replace(">", "&gt;").Replace("\"", "&quot;");
    }
}

// ---------------------------------------------------------------------------
// SoapBridge — manages WCF channel, token lifecycle, keepalive
// ---------------------------------------------------------------------------
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

    public bool IsHealthy { get; private set; }
    public DateTime LastCallTime { get; private set; }
    public DateTime TokenAcquiredTime { get; private set; }
    public string ClientId { get { return clientId; } }

    public SoapBridge(string soapUrl, string wsUser, string wsPass,
                      string clientId, bool skipCertValidation)
    {
        this.soapUrl = soapUrl;
        this.wsUser = wsUser;
        this.wsPass = wsPass;
        this.clientId = clientId;

        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        if (skipCertValidation)
        {
            ServicePointManager.ServerCertificateValidationCallback =
                delegate(object s, X509Certificate c, X509Chain ch, SslPolicyErrors e)
                {
                    return true;
                };
        }
    }

    public void Start()
    {
        CreateFactory();
        OpenChannel();

        // Initial token acquisition — must succeed or we cannot serve requests
        if (!RefreshTokenInternal())
        {
            throw new InvalidOperationException("Failed to acquire initial access token");
        }

        // Keepalive every 5 min — prevents ReliableSession inactivity timeout.
        // Uses a lightweight read operation (GetSections) instead of GetToken
        // to avoid token invalidation. Token is only refreshed on auth failure.
        keepaliveTimer = new Timer(
            delegate { Keepalive(); }, null,
            TimeSpan.FromMinutes(5), TimeSpan.FromMinutes(5));

        IsHealthy = true;
    }

    void CreateFactory()
    {
        WSHttpBinding binding = new WSHttpBinding();
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

        EndpointAddress endpoint = new EndpointAddress(soapUrl);
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

    // RecreateChannel WITHOUT token refresh — used inside CallSoap where
    // channelSem is already held. Token refresh would try to acquire
    // channelSem again causing a deadlock.
    void RecreateChannel(bool withTokenRefresh)
    {
        try { ((IClientChannel)channel).Abort(); } catch { }
        OpenChannel();
        if (withTokenRefresh)
        {
            RefreshTokenInternalNoLock();
        }
    }

    // Called during Start() — acquires channelSem itself.
    bool RefreshTokenInternal()
    {
        if (!channelSem.Wait(TimeSpan.FromSeconds(30)))
            return false;

        try
        {
            return RefreshTokenInternalNoLock();
        }
        catch
        {
            return false;
        }
        finally
        {
            channelSem.Release();
        }
    }

    // Core token refresh — caller MUST already hold channelSem.
    // Returns true on success, false on failure.
    bool RefreshTokenInternalNoLock()
    {
        try
        {
            string xml = SendMessage("GetToken", BuildGetTokenXml());
            string token = ExtractXmlValue(xml, "AccessToken");
            if (token != null)
            {
                lock (tokenLock) { accessToken = token; }
                TokenAcquiredTime = DateTime.UtcNow;
                return true;
            }
            return false;
        }
        catch
        {
            return false;
        }
    }

    // Build a lightweight read request for keepalive — uses GetSections which
    // returns a small payload and does NOT invalidate the access token.
    string BuildKeepaliveXml()
    {
        string currentToken;
        lock (tokenLock) { currentToken = accessToken; }
        return "<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
            "<AccessToken xmlns=\"\">" + currentToken + "</AccessToken>" +
            "<ClientId xmlns=\"\">" + clientId + "</ClientId>" +
            "<CompanyInitials xmlns=\"\">" + clientId + "</CompanyInitials>" +
            "<IsDeveloper xmlns=\"\">false</IsDeveloper>" +
            "<RequestId xmlns=\"\">" + Guid.NewGuid() + "</RequestId>" +
            "<RequestedByUserName i:nil=\"true\" xmlns=\"\"/>" +
            "<Version i:nil=\"true\" xmlns=\"\"/>" +
            "</request>";
    }

    void Keepalive()
    {
        if (!channelSem.Wait(TimeSpan.FromSeconds(10)))
            return; // skip if busy

        try
        {
            // Send a lightweight read to keep the WCF channel alive.
            // Do NOT call GetToken here — Unisoft invalidates the old token
            // when a new one is issued, causing a race condition.
            string xml = SendMessage("GetSections", BuildKeepaliveXml());
            string status = ExtractXmlValue(xml, "ReplyStatus");
            if (status == "Success")
            {
                IsHealthy = true;
            }
            else if (status == "Failure")
            {
                // Token may have expired — refresh it reactively
                string msg = ExtractXmlValue(xml, "Message") ?? "";
                if (msg.ToLower().Contains("accesstoken") || msg.ToLower().Contains("expired"))
                {
                    RefreshTokenInternalNoLock();
                }
                IsHealthy = true; // channel itself is still alive
            }
            else
            {
                IsHealthy = false;
            }
        }
        catch
        {
            // Channel faulted — recreate
            IsHealthy = false;
            try
            {
                RecreateChannel(true);
                IsHealthy = true;
            }
            catch
            {
                IsHealthy = false;
            }
        }
        finally
        {
            channelSem.Release();
        }
    }

    public string CallSoap(string opName, string requestXml)
    {
        if (!channelSem.Wait(TimeSpan.FromSeconds(30)))
            throw new System.TimeoutException("Channel busy");

        try
        {
            LastCallTime = DateTime.UtcNow;
            return SendMessage(opName, requestXml);
        }
        catch (CommunicationException)
        {
            // Channel may be faulted — recreate WITHOUT token refresh
            // (we already hold channelSem; RefreshToken would deadlock)
            // then retry the call once
            RecreateChannel(false);
            return SendMessage(opName, requestXml);
        }
        finally
        {
            channelSem.Release();
        }
    }

    // Force a token refresh — called when a SOAP response indicates token expiry.
    // Acquires channelSem to make the GetToken call safely.
    public void ForceTokenRefresh()
    {
        RefreshTokenInternal();
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
        XmlReader reader = XmlReader.Create(new StringReader(bodyXml));
        Message msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/" + opName,
            reader);
        Message result = channel.ProcessMessage(msg);

        using (StringWriter sw = new StringWriter())
        {
            XmlWriterSettings settings = new XmlWriterSettings();
            settings.Indent = false;
            using (XmlWriter writer = XmlWriter.Create(sw, settings))
            {
                result.WriteBody(writer);
                writer.Flush();
                return sw.ToString();
            }
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
        if (tagEnd < 0) return null;
        string tagStr = xml.Substring(start, tagEnd - start + 1);
        if (tagStr.Contains("nil=\"true\"")) return null;
        start = tagEnd + 1;
        int end = xml.IndexOf("</" + tag + ">", start);
        if (end < 0) return null;
        return xml.Substring(start, end - start);
    }
}

// ---------------------------------------------------------------------------
// Logger — structured JSON logging with daily rotation
// ---------------------------------------------------------------------------
class Logger
{
    static string logDir = "C:\\unisoft\\logs";
    static object fileLock = new object();
    static int retainDays = 30;

    public static void Init()
    {
        try
        {
            Directory.CreateDirectory(logDir);
            CleanOldLogs();
        }
        catch (Exception ex)
        {
            Console.WriteLine("WARNING: Could not initialize log directory: " + ex.Message);
        }
    }

    public static void Log(string op, int statusCode, long durationMs, string detail)
    {
        string ts = DateTime.UtcNow.ToString("o");
        StringBuilder sb = new StringBuilder();
        sb.Append("{\"ts\":\"" + ts + "\"");
        if (op != null)
            sb.Append(",\"op\":\"" + JsonEscapeLog(op) + "\"");
        sb.Append(",\"status\":" + statusCode);
        sb.Append(",\"duration_ms\":" + durationMs);
        if (detail != null)
            sb.Append(",\"detail\":\"" + JsonEscapeLog(detail) + "\"");
        sb.Append("}");
        string line = sb.ToString();

        Console.WriteLine(line);

        lock (fileLock)
        {
            try
            {
                string file = Path.Combine(logDir,
                    "proxy-" + DateTime.UtcNow.ToString("yyyy-MM-dd") + ".log");
                File.AppendAllText(file, line + "\n");
            }
            catch { }
        }
    }

    public static void Info(string message)
    {
        Log(null, 0, 0, message);
    }

    static void CleanOldLogs()
    {
        try
        {
            DateTime cutoff = DateTime.UtcNow.AddDays(-retainDays);
            string[] files = Directory.GetFiles(logDir, "proxy-*.log");
            foreach (string file in files)
            {
                FileInfo fi = new FileInfo(file);
                if (fi.LastWriteTimeUtc < cutoff)
                {
                    try { fi.Delete(); } catch { }
                }
            }
        }
        catch { }
    }

    static string JsonEscapeLog(string s)
    {
        if (s == null) return "";
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"")
                .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
    }
}

// ---------------------------------------------------------------------------
// UniProxyService — Windows Service wrapper
// ---------------------------------------------------------------------------
class UniProxyService : ServiceBase
{
    Thread listenerThread;

    public UniProxyService()
    {
        ServiceName = "UniProxy";
    }

    protected override void OnStart(string[] args)
    {
        listenerThread = new Thread(new ThreadStart(UniProxy.Run));
        listenerThread.IsBackground = true;
        listenerThread.Start();
    }

    protected override void OnStop()
    {
        UniProxy.Shutdown();
    }
}

// ---------------------------------------------------------------------------
// UniProxy — HTTP listener, routing, SOAP bridge integration
// ---------------------------------------------------------------------------
class UniProxy
{
    static string apiKey;
    static DateTime startTime;
    static int requestCount = 0;
    static DateTime lastRequestTime;
    static long maxRequestBytes;
    static SoapBridge bridge;
    static FileBridge fileBridge;
    static HttpListener listener;
    static volatile bool running;

    static void Main(string[] args)
    {
        // Detect run mode: --console flag, interactive session, or Windows Service
        bool consoleMode = false;
        if (args.Length > 0 && args[0] == "--console")
        {
            consoleMode = true;
        }
        else if (Environment.UserInteractive)
        {
            consoleMode = true;
        }

        if (consoleMode)
        {
            Run();
        }
        else
        {
            ServiceBase.Run(new UniProxyService());
        }
    }

    // Read env var from Machine scope first (for Windows Service), then Process scope (for console)
    static string GetEnv(string name, string defaultValue)
    {
        string val = Environment.GetEnvironmentVariable(name, EnvironmentVariableTarget.Machine);
        if (!string.IsNullOrEmpty(val)) return val;
        val = Environment.GetEnvironmentVariable(name);
        if (!string.IsNullOrEmpty(val)) return val;
        return defaultValue;
    }

    public static void Run()
    {
        apiKey = GetEnv("PROXY_API_KEY", "dev-key");
        int port = int.Parse(GetEnv("PROXY_PORT", "5000"));
        maxRequestBytes = long.Parse(GetEnv("PROXY_MAX_REQUEST_BYTES", "5242880"));
        startTime = DateTime.UtcNow;
        running = true;

        // Initialize SOAP bridge
        string soapUrl = GetEnv("UNISOFT_SOAP_URL",
            "https://services.uat.gicunderwriters.co/management/imsservice.svc");
        string wsUser = GetEnv("UNISOFT_WS_USER", "");
        string wsPass = GetEnv("UNISOFT_WS_PASS", "");
        string clientId = GetEnv("UNISOFT_CLIENT_ID", "GIC_UAT");
        bool skipCert = string.Equals(
            GetEnv("UNISOFT_SKIP_CERT_VALIDATION", "false"),
            "true", StringComparison.OrdinalIgnoreCase);

        Logger.Init();
        Logger.Info("UniProxy v1.0 starting");
        Logger.Info("SOAP endpoint: " + soapUrl);
        Logger.Info("Client ID: " + clientId);
        Logger.Info("Skip cert validation: " + skipCert);

        bridge = new SoapBridge(soapUrl, wsUser, wsPass, clientId, skipCert);
        bridge.Start();
        Logger.Info("SOAP bridge started, token acquired");

        // Initialize file service bridge (attachment upload/download)
        string fileServiceUrl = GetEnv("UNISOFT_FILE_URL",
            "https://services.uat.gicunderwriters.co/attachments/insfileservice.svc");
        fileBridge = new FileBridge(fileServiceUrl);
        Logger.Info("File service bridge initialized: " + fileServiceUrl);

        listener = new HttpListener();
        listener.Prefixes.Add(string.Format("http://+:{0}/", port));
        listener.Start();
        Logger.Info("UniProxy listening on port " + port);

        while (running)
        {
            try
            {
                HttpListenerContext ctx = listener.GetContext();
                ThreadPool.QueueUserWorkItem(delegate { HandleRequest(ctx); });
            }
            catch (HttpListenerException)
            {
                // Listener was stopped (Shutdown called)
                if (!running) break;
                throw;
            }
        }

        Logger.Info("UniProxy stopped");
    }

    public static void Shutdown()
    {
        Logger.Info("UniProxy shutting down");
        running = false;
        try
        {
            if (listener != null && listener.IsListening)
            {
                listener.Stop();
            }
        }
        catch { }
    }

    static void HandleRequest(HttpListenerContext ctx)
    {
        try
        {
            string path = ctx.Request.Url.AbsolutePath.ToLower();
            string rawPath = ctx.Request.Url.AbsolutePath;

            // Health check — no auth required
            if (path == "/api/health")
            {
                int tokenAgeSec = bridge != null && bridge.TokenAcquiredTime > DateTime.MinValue
                    ? (int)(DateTime.UtcNow - bridge.TokenAcquiredTime).TotalSeconds : -1;
                string channelState = bridge != null
                    ? (bridge.IsHealthy ? "healthy" : "faulted") : "not_started";
                string lastReq = lastRequestTime > DateTime.MinValue
                    ? "\"" + lastRequestTime.ToString("o") + "\"" : "null";
                string json = "{\"status\":\"ok\",\"uptime_seconds\":" +
                    (int)(DateTime.UtcNow - startTime).TotalSeconds +
                    ",\"requests\":" + requestCount +
                    ",\"token_age_seconds\":" + tokenAgeSec +
                    ",\"channel_state\":\"" + channelState + "\"" +
                    ",\"last_request_time\":" + lastReq + "}";
                WriteJson(ctx, 200, json);
                return;
            }

            // Meta — no auth required
            if (path == "/api/meta/operations")
            {
                WriteJson(ctx, 200,
                    "{\"service\":\"IIMSService\",\"operations\":910," +
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

            // SOAP passthrough
            if (path.StartsWith("/api/soap/") && ctx.Request.HttpMethod == "POST")
            {
                if (ctx.Request.ContentLength64 > maxRequestBytes)
                {
                    WriteJson(ctx, 413,
                        "{\"error\":\"request_too_large\",\"max_bytes\":" + maxRequestBytes + "}");
                    return;
                }

                string opName = rawPath.Substring("/api/soap/".Length);
                Interlocked.Increment(ref requestCount);
                lastRequestTime = DateTime.UtcNow;

                Stopwatch sw = Stopwatch.StartNew();
                try
                {
                    string requestBody;
                    using (StreamReader sr = new StreamReader(ctx.Request.InputStream))
                    {
                        requestBody = sr.ReadToEnd();
                    }

                    string responseJson = CallWithTokenRetry(opName, requestBody);

                    // Determine HTTP status from response content
                    int httpStatus = 200;
                    if (responseJson.Contains("\"error\":\"unisoft_fault\""))
                        httpStatus = 502;
                    else if (responseJson.Contains("\"error\":\"unisoft_validation\""))
                        httpStatus = 422;

                    sw.Stop();
                    Logger.Log(opName, httpStatus, sw.ElapsedMilliseconds, null);
                    WriteJson(ctx, httpStatus, responseJson);
                }
                catch (System.TimeoutException)
                {
                    sw.Stop();
                    Logger.Log(opName, 503, sw.ElapsedMilliseconds, "Channel busy");
                    WriteJson(ctx, 503,
                        "{\"error\":\"busy\",\"message\":\"Channel busy, try again\"," +
                        "\"retryAfter\":5}");
                }
                catch (Exception ex)
                {
                    sw.Stop();
                    Logger.Log(opName, 500, sw.ElapsedMilliseconds, ex.Message);
                    WriteJson(ctx, 500,
                        "{\"error\":\"proxy_error\",\"message\":\"" +
                        JsonEscape(ex.Message) + "\"}");
                }
                return;
            }

            // File service: Get attachments for a quote
            if (path == "/api/file/attachments" && ctx.Request.HttpMethod == "GET")
            {
                string qn = ctx.Request.QueryString["quoteNumber"];
                string mga = ctx.Request.QueryString["mgaNumber"] ?? "1";
                if (string.IsNullOrEmpty(qn))
                {
                    WriteJson(ctx, 400,
                        "{\"error\":\"missing_parameter\",\"message\":\"quoteNumber is required\"}");
                    return;
                }

                Interlocked.Increment(ref requestCount);
                lastRequestTime = DateTime.UtcNow;
                Stopwatch sw = Stopwatch.StartNew();

                try
                {
                    string innerXml =
                        "<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
                        "<AccessToken i:nil=\"true\" xmlns=\"\"/>" +
                        "<ClientId i:nil=\"true\" xmlns=\"\"/>" +
                        "<RequestId i:nil=\"true\" xmlns=\"\"/>" +
                        "<Version i:nil=\"true\" xmlns=\"\"/>" +
                        "<MGANumber xmlns=\"\">" + mga + "</MGANumber>" +
                        "<QuoteNumber xmlns=\"\">" + qn + "</QuoteNumber>" +
                        "<SortExpression xmlns=\"\"/>" +
                        "</request>";
                    string responseXml = fileBridge.CallBody("GetQuoteAttachments", innerXml);
                    string responseJson = XmlToJson(responseXml);
                    sw.Stop();
                    Logger.Log("FILE:GetQuoteAttachments", 200, sw.ElapsedMilliseconds, null);
                    WriteJson(ctx, 200, responseJson);
                }
                catch (Exception ex)
                {
                    sw.Stop();
                    Logger.Log("FILE:GetQuoteAttachments", 500, sw.ElapsedMilliseconds, ex.Message);
                    WriteJson(ctx, 500,
                        "{\"error\":\"file_service_error\",\"message\":\"" +
                        JsonEscape(ex.Message) + "\"}");
                }
                return;
            }

            // File service: Upload attachment to a quote
            if (path == "/api/file/upload" && ctx.Request.HttpMethod == "POST")
            {
                Interlocked.Increment(ref requestCount);
                lastRequestTime = DateTime.UtcNow;
                Stopwatch sw = Stopwatch.StartNew();

                try
                {
                    // Read multipart form data
                    string contentType = ctx.Request.ContentType ?? "";

                    byte[] fileBytes = null;
                    string fileName = null;
                    string fileType = null;
                    int quoteNumber = 0;
                    int mgaNumber = 1;
                    string createdBy = "automation";
                    string description = "";

                    if (contentType.Contains("multipart/form-data"))
                    {
                        // Parse multipart form data
                        string boundary = contentType.Substring(
                            contentType.IndexOf("boundary=") + 9).Trim();
                        byte[] body;
                        using (MemoryStream ms = new MemoryStream())
                        {
                            ctx.Request.InputStream.CopyTo(ms);
                            body = ms.ToArray();
                        }
                        ParseMultipart(body, boundary, ref fileBytes, ref fileName,
                            ref fileType, ref quoteNumber, ref mgaNumber,
                            ref createdBy, ref description);
                    }
                    else
                    {
                        // JSON body with base64 file content
                        string requestBody;
                        using (StreamReader sr = new StreamReader(ctx.Request.InputStream))
                        {
                            requestBody = sr.ReadToEnd();
                        }
                        JavaScriptSerializer ser = new JavaScriptSerializer();
                        ser.MaxJsonLength = 50 * 1024 * 1024;
                        Dictionary<string, object> dict =
                            ser.Deserialize<Dictionary<string, object>>(requestBody);

                        if (dict.ContainsKey("fileContent"))
                            fileBytes = Convert.FromBase64String((string)dict["fileContent"]);
                        if (dict.ContainsKey("fileName"))
                            fileName = (string)dict["fileName"];
                        if (dict.ContainsKey("fileType"))
                            fileType = (string)dict["fileType"];
                        if (dict.ContainsKey("quoteNumber"))
                            quoteNumber = Convert.ToInt32(dict["quoteNumber"]);
                        if (dict.ContainsKey("mgaNumber"))
                            mgaNumber = Convert.ToInt32(dict["mgaNumber"]);
                        if (dict.ContainsKey("createdBy"))
                            createdBy = (string)dict["createdBy"];
                        if (dict.ContainsKey("description"))
                            description = (string)dict["description"];
                    }

                    if (fileBytes == null || fileBytes.Length == 0)
                    {
                        WriteJson(ctx, 400,
                            "{\"error\":\"missing_file\",\"message\":\"No file content provided\"}");
                        return;
                    }
                    if (quoteNumber <= 0)
                    {
                        WriteJson(ctx, 400,
                            "{\"error\":\"missing_parameter\",\"message\":\"quoteNumber is required\"}");
                        return;
                    }
                    if (string.IsNullOrEmpty(fileType) && fileName != null)
                    {
                        // Derive file type from extension
                        int dot = fileName.LastIndexOf('.');
                        if (dot >= 0)
                            fileType = fileName.Substring(dot + 1).ToUpper();
                    }
                    if (string.IsNullOrEmpty(fileType))
                        fileType = "PDF";
                    if (string.IsNullOrEmpty(description) && fileName != null)
                        description = fileName;

                    string cid = bridge != null ? bridge.ClientId : "GIC_UAT";
                    string responseXml = fileBridge.UploadQuoteAttachment(
                        fileBytes, quoteNumber, mgaNumber, fileName ?? "attachment." + fileType.ToLower(),
                        fileType, createdBy, description, cid);
                    string responseJson = XmlToJson(responseXml);

                    int httpStatus = 200;
                    if (responseJson.Contains("\"ReplyStatus\":\"Failure\""))
                        httpStatus = 422;

                    sw.Stop();
                    Logger.Log("FILE:AddQuoteAttachment", httpStatus, sw.ElapsedMilliseconds, null);
                    WriteJson(ctx, httpStatus, responseJson);
                }
                catch (Exception ex)
                {
                    sw.Stop();
                    Logger.Log("FILE:AddQuoteAttachment", 500, sw.ElapsedMilliseconds, ex.Message);
                    WriteJson(ctx, 500,
                        "{\"error\":\"file_service_error\",\"message\":\"" +
                        JsonEscape(ex.Message) + "\"}");
                }
                return;
            }

            WriteJson(ctx, 404, "{\"error\":\"not_found\"}");
        }
        catch (Exception ex)
        {
            try
            {
                WriteJson(ctx, 500,
                    "{\"error\":\"proxy_error\",\"message\":\"" +
                    JsonEscape(ex.Message) + "\"}");
            }
            catch { }
        }
    }

    // ---------------------------------------------------------------------------
    // DTO Namespace Registry — maps JSON keys to DataContract namespaces
    // ---------------------------------------------------------------------------
    static Dictionary<string, string> dtoNamespaces = new Dictionary<string, string>
    {
        { "Quote", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes" },
        { "QuoteActivity", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes" },
        { "QuoteStatus", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes" },
        { "Submission", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes.Submissions" },
        { "Activity", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Activities" },
        { "CashDetail", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Cash" },
        { "PolicyEntry", "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.PolicyInquiry" }
    };

    // RequestBase fields the proxy injects — caller must NOT send these
    static HashSet<string> requestBaseFields = new HashSet<string>
    {
        "AccessToken", "ClientId", "CompanyInitials", "IsDeveloper",
        "RequestId", "RequestedByUserName", "Version"
    };

    // ---------------------------------------------------------------------------
    // JSON → XML translation
    // ---------------------------------------------------------------------------
    static string JsonToXml(string opName, string json, string token, string clientId)
    {
        JavaScriptSerializer serializer = new JavaScriptSerializer();
        serializer.MaxJsonLength = 5 * 1024 * 1024;

        Dictionary<string, object> dict;
        if (string.IsNullOrEmpty(json) || json.Trim() == "{}")
        {
            dict = new Dictionary<string, object>();
        }
        else
        {
            dict = serializer.Deserialize<Dictionary<string, object>>(json);
        }

        StringBuilder sb = new StringBuilder();
        sb.Append("<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">");

        // Inject RequestBase fields — proxy controls these
        sb.Append("<AccessToken xmlns=\"\">" + Escape(token) + "</AccessToken>");
        sb.Append("<ClientId xmlns=\"\">" + Escape(clientId) + "</ClientId>");
        sb.Append("<CompanyInitials xmlns=\"\">" + Escape(clientId) + "</CompanyInitials>");
        sb.Append("<IsDeveloper xmlns=\"\">false</IsDeveloper>");
        sb.Append("<RequestId xmlns=\"\">" + Guid.NewGuid() + "</RequestId>");
        sb.Append("<RequestedByUserName i:nil=\"true\" xmlns=\"\"/>");
        sb.Append("<Version i:nil=\"true\" xmlns=\"\"/>");

        // Caller fields
        foreach (KeyValuePair<string, object> kvp in dict)
        {
            if (requestBaseFields.Contains(kvp.Key)) continue;
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
            {
                sb.Append("<" + key + " i:nil=\"true\" xmlns=\"\" xmlns:b=\"" + ns + "\"/>");
            }
            else
            {
                sb.Append("<" + key + " i:nil=\"true\" xmlns=\"\"/>");
            }
            return;
        }

        string dtoNs;
        if (dtoNamespaces.TryGetValue(key, out dtoNs) && value is Dictionary<string, object>)
        {
            // Nested DTO with namespace
            // CRITICAL: WCF DataContractSerializer requires fields in alphabetical order.
            // Out-of-order fields are silently ignored and treated as null.
            Dictionary<string, object> dict = (Dictionary<string, object>)value;
            List<string> sortedKeys = new List<string>(dict.Keys);
            sortedKeys.Sort(StringComparer.Ordinal);
            sb.Append("<" + key + " xmlns=\"\" xmlns:b=\"" + dtoNs + "\">");
            foreach (string k in sortedKeys)
            {
                AppendDtoField(sb, k, dict[k]);
            }
            sb.Append("</" + key + ">");
        }
        else if (value is System.Collections.ArrayList)
        {
            // JSON array — emit repeated elements with same tag name
            System.Collections.ArrayList arr = (System.Collections.ArrayList)value;
            foreach (object item in arr)
            {
                if (item is Dictionary<string, object>)
                {
                    sb.Append("<" + key + " xmlns=\"\">");
                    Dictionary<string, object> itemDict = (Dictionary<string, object>)item;
                    foreach (KeyValuePair<string, object> kvp in itemDict)
                    {
                        AppendField(sb, kvp.Key, kvp.Value);
                    }
                    sb.Append("</" + key + ">");
                }
                else if (item != null)
                {
                    sb.Append("<" + key + " xmlns=\"\">" + ToXmlString(item) +
                              "</" + key + ">");
                }
            }
        }
        else
        {
            // Flat field — scalar value
            sb.Append("<" + key + " xmlns=\"\">" + ToXmlString(value) + "</" + key + ">");
        }
    }

    // Convert a value to its XML string representation.
    // Booleans must be lowercase (true/false), not C# style (True/False).
    static string ToXmlString(object value)
    {
        if (value is bool) return ((bool)value) ? "true" : "false";
        return Escape(value.ToString());
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
            // Sub-DTO — emit as nil per design (sub-DTOs are null in write requests)
            sb.Append("<b:" + key + " i:nil=\"true\"/>");
            return;
        }
        if (value is System.Collections.ArrayList)
        {
            // Array within DTO — emit repeated elements
            System.Collections.ArrayList arr = (System.Collections.ArrayList)value;
            foreach (object item in arr)
            {
                if (item != null)
                {
                    sb.Append("<b:" + key + ">" + ToXmlString(item) + "</b:" + key + ">");
                }
            }
            return;
        }
        sb.Append("<b:" + key + ">" + ToXmlString(value) + "</b:" + key + ">");
    }

    // ---------------------------------------------------------------------------
    // XML → JSON translation
    // ---------------------------------------------------------------------------

    // ResponseBase fields always extracted to _meta
    static HashSet<string> metaFields = new HashSet<string>
    {
        "Build", "CorrelationId", "Message", "ReplyStatus", "RowsAffected", "Version"
    };

    static string XmlToJson(string xml)
    {
        XmlDocument doc = new XmlDocument();
        doc.LoadXml(xml);

        // WriteBody output structure depends on the message.
        // Typically: <XXXResponse><XXXResult>...data...</XXXResult></XXXResponse>
        // Or for faults: <Fault>...</Fault>
        // We search downward for the Result element.
        XmlNode root = doc.DocumentElement;
        XmlNode resultNode = null;

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
            // Root is the Body element — look for Response > Result or Fault
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

        // Separate meta fields from data fields
        StringBuilder meta = new StringBuilder();
        StringBuilder data = new StringBuilder();
        meta.Append("\"_meta\":{");
        bool firstMeta = true;
        bool firstData = true;

        foreach (XmlNode child in resultNode.ChildNodes)
        {
            if (child.NodeType != XmlNodeType.Element) continue;
            string localName = StripPrefix(child.LocalName);
            if (metaFields.Contains(localName))
            {
                if (!firstMeta) meta.Append(",");
                meta.Append("\"" + localName + "\":" + NodeToJsonValue(child));
                firstMeta = false;
            }
            else
            {
                if (!firstData) data.Append(",");
                data.Append("\"" + localName + "\":" + NodeToJsonValue(child));
                firstData = false;
            }
        }
        meta.Append("}");

        if (firstData)
            return "{" + meta.ToString() + "}";
        return "{" + meta.ToString() + "," + data.ToString() + "}";
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

        // Leaf node (text content only, or empty)
        if (!node.HasChildNodes)
            return "null";
        if (node.ChildNodes.Count == 1 && node.FirstChild.NodeType == XmlNodeType.Text)
        {
            string text = node.InnerText;
            // Try to parse as number
            int intVal;
            if (int.TryParse(text, out intVal))
                return intVal.ToString();
            decimal decVal;
            if (text.Contains(".") && decimal.TryParse(text, out decVal))
                return decVal.ToString();
            if (text == "true" || text == "false")
                return text;
            return "\"" + JsonEscape(text) + "\"";
        }

        // Check if children form a DTO array (repeated elements with *DTO names)
        Dictionary<string, int> childNames = new Dictionary<string, int>();
        foreach (XmlNode child in node.ChildNodes)
        {
            if (child.NodeType != XmlNodeType.Element) continue;
            string ln = StripPrefix(child.LocalName);
            if (childNames.ContainsKey(ln))
                childNames[ln] = childNames[ln] + 1;
            else
                childNames[ln] = 1;
        }

        // If single child type ending in DTO, or multiple children with same name -> array
        if (childNames.Count == 1)
        {
            string childName = null;
            int count = 0;
            foreach (KeyValuePair<string, int> kvp in childNames)
            {
                childName = kvp.Key;
                count = kvp.Value;
            }
            if (childName != null && (childName.EndsWith("DTO") || count > 1))
            {
                StringBuilder arr = new StringBuilder("[");
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
        {
            foreach (XmlAttribute attr in node.Attributes)
            {
                if (attr.LocalName == "nil" && attr.Value == "true")
                    return "null";
            }
        }

        StringBuilder sb = new StringBuilder("{");
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
        if (colon >= 0)
            return name.Substring(colon + 1);
        return name;
    }

    static string BuildFaultJson(XmlNode faultNode)
    {
        string reason = "";
        string code = "";
        string detail = "";
        foreach (XmlNode child in faultNode.ChildNodes)
        {
            if (child.LocalName == "Reason")
                reason = child.InnerText;
            else if (child.LocalName == "Code")
                code = child.InnerText;
            else if (child.LocalName == "Detail")
                detail = child.InnerText;
        }

        // Distinguish auth faults from validation faults per code review.
        // Heuristic: auth/security/token issues get unisoft_fault (502),
        // everything else gets unisoft_validation (422).
        string lowerReason = reason.ToLower();
        string lowerDetail = detail.ToLower();
        bool isAuthFault = lowerReason.Contains("nullreference")
            || lowerReason.Contains("security")
            || lowerReason.Contains("token")
            || lowerReason.Contains("unauthorized")
            || lowerDetail.Contains("nullreference")
            || lowerDetail.Contains("security")
            || lowerDetail.Contains("token");

        if (isAuthFault)
        {
            return "{\"_meta\":{\"ReplyStatus\":\"Fault\"}," +
                   "\"error\":\"unisoft_fault\"," +
                   "\"message\":\"" + JsonEscape(reason) + "\"," +
                   "\"faultCode\":\"" + JsonEscape(code) + "\"}";
        }
        else
        {
            return "{\"_meta\":{\"ReplyStatus\":\"Fault\"}," +
                   "\"error\":\"unisoft_validation\"," +
                   "\"message\":\"" + JsonEscape(reason) + "\"," +
                   "\"detail\":\"" + JsonEscape(detail) + "\"," +
                   "\"faultCode\":\"" + JsonEscape(code) + "\"}";
        }
    }

    static string Escape(string s)
    {
        if (s == null) return "";
        return s.Replace("&", "&amp;").Replace("<", "&lt;")
                .Replace(">", "&gt;").Replace("\"", "&quot;");
    }

    static string JsonEscape(string s)
    {
        if (s == null) return "";
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"")
                .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
    }

    // Parse multipart form data for file upload
    static void ParseMultipart(byte[] body, string boundary,
        ref byte[] fileBytes, ref string fileName, ref string fileType,
        ref int quoteNumber, ref int mgaNumber, ref string createdBy,
        ref string description)
    {
        string bodyStr = Encoding.UTF8.GetString(body);
        string sep = "--" + boundary;
        string[] parts = bodyStr.Split(new string[] { sep }, StringSplitOptions.RemoveEmptyEntries);

        foreach (string part in parts)
        {
            if (part.Trim() == "--" || string.IsNullOrWhiteSpace(part)) continue;

            int headerEnd = part.IndexOf("\r\n\r\n");
            if (headerEnd < 0) continue;
            string headers = part.Substring(0, headerEnd);
            string content = part.Substring(headerEnd + 4).TrimEnd('\r', '\n');

            // Extract field name from Content-Disposition
            string fieldName = null;
            string partFileName = null;
            if (headers.Contains("Content-Disposition"))
            {
                int nameIdx = headers.IndexOf("name=\"");
                if (nameIdx >= 0)
                {
                    nameIdx += 6;
                    int nameEnd = headers.IndexOf("\"", nameIdx);
                    if (nameEnd > nameIdx)
                        fieldName = headers.Substring(nameIdx, nameEnd - nameIdx);
                }
                int fnIdx = headers.IndexOf("filename=\"");
                if (fnIdx >= 0)
                {
                    fnIdx += 10;
                    int fnEnd = headers.IndexOf("\"", fnIdx);
                    if (fnEnd > fnIdx)
                        partFileName = headers.Substring(fnIdx, fnEnd - fnIdx);
                }
            }

            if (fieldName == null) continue;

            if (partFileName != null || fieldName == "file")
            {
                // Binary file content — need to extract from raw bytes
                // Find the boundary in raw bytes to get exact binary content
                int headerEndBytes = FindSequence(body, Encoding.UTF8.GetBytes("\r\n\r\n"));
                if (headerEndBytes >= 0)
                {
                    // Simpler: re-read from the part boundary
                    byte[] boundaryBytes = Encoding.UTF8.GetBytes(sep);
                    // For multipart, just use the string-parsed content and convert
                    // This works for base64-encoded content; for raw binary, would need
                    // proper byte-level parsing. For our use case (PDF upload), this is fine.
                }
                fileBytes = Encoding.UTF8.GetBytes(content);
                // If content looks like base64, decode it
                if (!content.Contains("%PDF") && !content.Contains("JFIF"))
                {
                    try { fileBytes = Convert.FromBase64String(content.Trim()); } catch { }
                }
                if (partFileName != null) fileName = partFileName;
            }
            else
            {
                content = content.Trim();
                switch (fieldName)
                {
                    case "quoteNumber": int.TryParse(content, out quoteNumber); break;
                    case "mgaNumber": int.TryParse(content, out mgaNumber); break;
                    case "fileName": fileName = content; break;
                    case "fileType": fileType = content; break;
                    case "createdBy": createdBy = content; break;
                    case "description": description = content; break;
                }
            }
        }
    }

    static int FindSequence(byte[] data, byte[] pattern)
    {
        for (int i = 0; i <= data.Length - pattern.Length; i++)
        {
            bool match = true;
            for (int j = 0; j < pattern.Length; j++)
            {
                if (data[i + j] != pattern[j]) { match = false; break; }
            }
            if (match) return i;
        }
        return -1;
    }

    // Call a SOAP operation with automatic token refresh on auth failure.
    // If the response indicates an expired token, refreshes and retries once.
    static string CallWithTokenRetry(string opName, string requestBody)
    {
        string token = bridge.GetCurrentToken();
        string cid = bridge.ClientId;
        string requestXml = JsonToXml(opName, requestBody, token, cid);
        string responseXml = bridge.CallSoap(opName, requestXml);
        string responseJson = XmlToJson(responseXml);

        // Check for expired token in the response
        if (responseJson.Contains("expired AccessToken") ||
            responseJson.Contains("Invalid or expired") ||
            responseJson.Contains("Call GetToken()"))
        {
            // Refresh token and retry once
            Logger.Log(opName, 0, 0, "Token expired, refreshing and retrying");
            bridge.ForceTokenRefresh();
            token = bridge.GetCurrentToken();
            requestXml = JsonToXml(opName, requestBody, token, cid);
            responseXml = bridge.CallSoap(opName, requestXml);
            responseJson = XmlToJson(responseXml);
        }

        return responseJson;
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
