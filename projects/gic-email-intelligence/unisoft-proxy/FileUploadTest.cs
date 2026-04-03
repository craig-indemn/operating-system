// Test using EXACT formats from Fiddler captures.
// GetQuoteAttachments: request wrapper in body
// AddQuoteAttachment: metadata in SOAP headers, file stream in body
// Compile: csc.exe /out:FileUploadTest.exe /reference:System.ServiceModel.dll /reference:System.Runtime.Serialization.dll /reference:System.Xml.dll FileUploadTest.cs

using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.ServiceModel.Description;
using System.ServiceModel.Dispatcher;
using System.Text;
using System.Xml;

[ServiceContract(Namespace = "http://tempuri.org/")]
interface IIMSService
{
    [OperationContract(Action = "http://tempuri.org/IIMSService/GetToken",
                       ReplyAction = "http://tempuri.org/IIMSService/GetTokenResponse")]
    Message GetToken(Message request);
}

[ServiceContract(Namespace = "http://tempuri.org/")]
interface IINSFileService
{
    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

class MustUnderstandInspector : IClientMessageInspector
{
    public object BeforeSendRequest(ref Message request, IClientChannel channel) { return null; }
    public void AfterReceiveReply(ref Message reply, object correlationState)
    {
        for (int i = 0; i < reply.Headers.Count; i++)
            if (reply.Headers[i].MustUnderstand)
                reply.Headers.UnderstoodHeaders.Add(reply.Headers[i]);
    }
}

class MustUnderstandBehavior : IEndpointBehavior
{
    public void AddBindingParameters(ServiceEndpoint e, BindingParameterCollection p) { }
    public void ApplyClientBehavior(ServiceEndpoint e, ClientRuntime r)
    { r.ClientMessageInspectors.Add(new MustUnderstandInspector()); }
    public void ApplyDispatchBehavior(ServiceEndpoint e, EndpointDispatcher d) { }
    public void Validate(ServiceEndpoint e) { }
}

class FileUploadTest
{
    static string soapUrl = "https://services.uat.gicunderwriters.co/management/imsservice.svc";
    static string fileUrl = "https://services.uat.gicunderwriters.co/attachments/insfileservice.svc";
    static string wsUser = "UniClient";
    static string wsPass = "J5j!}7=r/z";
    static string clientId = "GIC_UAT";
    static string dtoNs = "http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Attachments.Services.DTO";

    static void Main()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };

        Console.WriteLine("=== Exact Fiddler Format Test ===");
        string token = GetIMSToken();
        if (token == null) { Console.WriteLine("FAILED to get token"); return; }
        Console.WriteLine("Token: " + token.Substring(0, 8) + "...\n");

        // Test 1: GetQuoteAttachments — exact Fiddler format (request in body, nil tokens)
        Console.WriteLine("=== GetQuoteAttachments (exact Fiddler format) ===");
        CallFileBody("GetQuoteAttachments",
            "<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
            "<AccessToken i:nil=\"true\" xmlns=\"\"/>" +
            "<ClientId i:nil=\"true\" xmlns=\"\"/>" +
            "<RequestId i:nil=\"true\" xmlns=\"\"/>" +
            "<Version i:nil=\"true\" xmlns=\"\"/>" +
            "<MGANumber xmlns=\"\">1</MGANumber>" +
            "<QuoteNumber xmlns=\"\">17140</QuoteNumber>" +
            "<SortExpression xmlns=\"\"/>" +
            "</request>");

        // Test 2: AddQuoteAttachment — metadata in HEADERS, file in body
        Console.WriteLine("\n=== AddQuoteAttachment (headers + body, exact Fiddler format) ===");
        byte[] testPdf = Encoding.UTF8.GetBytes("%PDF-1.0 test upload from automation");
        CallFileWithHeaders("AddQuoteAttachment", testPdf,
            17140, 1, "test-automation.pdf", "PDF", "ccerto", "Test from automation probe");
    }

    // Standard body-based call (for GetQuoteAttachments etc.)
    static void CallFileBody(string op, string innerXml)
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MessageEncoding = WSMessageEncoding.Mtom;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        b.SendTimeout = TimeSpan.FromSeconds(60);

        ChannelFactory<IINSFileService> f = new ChannelFactory<IINSFileService>(b, new EndpointAddress(fileUrl));
        f.Endpoint.EndpointBehaviors.Add(new MustUnderstandBehavior());
        IINSFileService ch = f.CreateChannel();

        try
        {
            ((IClientChannel)ch).Open();
            string body = "<" + op + " xmlns=\"http://tempuri.org/\">" + innerXml + "</" + op + ">";
            Message req = Message.CreateMessage(MessageVersion.Soap11,
                "http://tempuri.org/IINSFileService/" + op,
                XmlReader.Create(new StringReader(body)));
            Message resp = ch.ProcessMessage(req);
            string r = ReadBody(resp);
            Console.WriteLine(r.Length > 1000 ? r.Substring(0, 1000) + "\n...(" + r.Length + " chars)" : r);
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.GetType().Name + ": " + ex.Message);
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            try { f.Close(); } catch { }
        }
    }

    // Header-based call for AddQuoteAttachment (message contract pattern)
    static void CallFileWithHeaders(string op, byte[] fileBytes,
        int quoteNumber, int mgaNumber, string fileName, string fileType,
        string createdBy, string description)
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MessageEncoding = WSMessageEncoding.Mtom;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        b.SendTimeout = TimeSpan.FromSeconds(60);
        b.TransferMode = TransferMode.Streamed;

        ChannelFactory<IINSFileService> f = new ChannelFactory<IINSFileService>(b, new EndpointAddress(fileUrl));
        f.Endpoint.EndpointBehaviors.Add(new MustUnderstandBehavior());
        IINSFileService ch = f.CreateChannel();

        try
        {
            ((IClientChannel)ch).Open();

            // Body: QuoteAttachmentAddRequest with FileByteStream (base64 for now)
            string bodyXml = "<QuoteAttachmentAddRequest xmlns=\"http://tempuri.org/\">" +
                "<FileByteStream>" + Convert.ToBase64String(fileBytes) + "</FileByteStream>" +
                "</QuoteAttachmentAddRequest>";

            Message req = Message.CreateMessage(MessageVersion.Soap11,
                "http://tempuri.org/IINSFileService/" + op,
                XmlReader.Create(new StringReader(bodyXml)));

            // Add SOAP headers matching the Fiddler capture
            string ns = "http://tempuri.org/";
            string xsi = "http://www.w3.org/2001/XMLSchema-instance";

            // AccessToken header (nil)
            req.Headers.Add(MessageHeader.CreateHeader("AccessToken", ns,
                null, true));

            // ClientId header
            req.Headers.Add(MessageHeader.CreateHeader("ClientId", ns,
                clientId, true));

            // RequestId header
            req.Headers.Add(MessageHeader.CreateHeader("RequestId", ns,
                Guid.NewGuid().ToString(), true));

            // Version header (nil)
            req.Headers.Add(MessageHeader.CreateHeader("Version", ns,
                null, true));

            // QuoteAttachment header — the DTO with metadata
            // Build as raw XML
            string attXml = "<QuoteAttachment xmlns:i=\"" + xsi + "\" xmlns:d=\"" + dtoNs + "\">" +
                "<d:AttachmentType i:nil=\"true\"/>" +
                "<d:CreatedByUser>" + createdBy + "</d:CreatedByUser>" +
                "<d:CreatedDate>" + DateTime.UtcNow.ToString("o") + "</d:CreatedDate>" +
                "<d:CurrentCategory>" +
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
                "</d:CurrentCategory>" +
                "<d:Description>" + description + "</d:Description>" +
                "<d:FileName i:nil=\"true\"/>" +
                "<d:FileType>" + fileType + "</d:FileType>" +
                "<d:FileTypeDescription i:nil=\"true\"/>" +
                "<d:Id>0</d:Id>" +
                "<d:IsPublic>false</d:IsPublic>" +
                "<d:MGANumber>" + mgaNumber + "</d:MGANumber>" +
                "<d:QuoteNumber>" + quoteNumber + "</d:QuoteNumber>" +
                "<d:Source i:nil=\"true\"/>" +
                "<d:Url i:nil=\"true\"/>" +
                "</QuoteAttachment>";

            // Add as raw XML header
            XmlDocument doc = new XmlDocument();
            doc.LoadXml(attXml);
            req.Headers.Add(new XmlDocumentHeader(doc.DocumentElement, ns, true));

            Message resp = ch.ProcessMessage(req);
            string r = ReadBody(resp);
            Console.WriteLine(r.Length > 1000 ? r.Substring(0, 1000) + "\n...(" + r.Length + " chars)" : r);
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.GetType().Name + ": " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("  Inner: " + ex.InnerException.Message);
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            try { f.Close(); } catch { }
        }
    }

    static string GetIMSToken()
    {
        WSHttpBinding b = new WSHttpBinding();
        b.Security.Mode = SecurityMode.TransportWithMessageCredential;
        b.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
        b.Security.Message.EstablishSecurityContext = true;
        b.ReliableSession.Enabled = true;
        ChannelFactory<IIMSService> f = new ChannelFactory<IIMSService>(b, new EndpointAddress(soapUrl));
        f.Credentials.UserName.UserName = wsUser;
        f.Credentials.UserName.Password = wsPass;
        IIMSService ch = f.CreateChannel();
        ((IClientChannel)ch).Open();
        try
        {
            string xml = "<request xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
                "<AccessToken i:nil=\"true\" xmlns=\"\"/>" +
                "<ClientId xmlns=\"\">" + clientId + "</ClientId>" +
                "<CompanyInitials xmlns=\"\">" + clientId + "</CompanyInitials>" +
                "<IsDeveloper xmlns=\"\">false</IsDeveloper>" +
                "<RequestId xmlns=\"\">" + Guid.NewGuid() + "</RequestId>" +
                "<RequestedByUserName i:nil=\"true\" xmlns=\"\"/>" +
                "<Version i:nil=\"true\" xmlns=\"\"/></request>";
            string body = "<GetToken xmlns=\"http://tempuri.org/\">" + xml + "</GetToken>";
            Message req = Message.CreateMessage(MessageVersion.Soap12WSAddressing10,
                "http://tempuri.org/IIMSService/GetToken", XmlReader.Create(new StringReader(body)));
            Message resp = ch.GetToken(req);
            string r = ReadBody(resp);
            string search = "<AccessToken xmlns=\"\">";
            int s = r.IndexOf(search);
            if (s >= 0) { s += search.Length; int e = r.IndexOf("</AccessToken>", s); if (e > s) return r.Substring(s, e - s); }
            return null;
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            f.Close();
        }
    }

    static string ReadBody(Message msg)
    {
        StringBuilder sb = new StringBuilder();
        using (XmlWriter w = XmlWriter.Create(sb)) { msg.WriteBody(w); w.Flush(); }
        return sb.ToString();
    }
}

// Custom header that writes raw XML
class XmlDocumentHeader : MessageHeader
{
    XmlElement element;
    string headerNs;
    bool mustUnderstand;

    public XmlDocumentHeader(XmlElement element, string ns, bool mustUnderstand)
    {
        this.element = element;
        this.headerNs = ns;
        this.mustUnderstand = mustUnderstand;
    }

    public override string Name { get { return element.LocalName; } }
    public override string Namespace { get { return headerNs; } }
    public override bool MustUnderstand { get { return mustUnderstand; } }

    protected override void OnWriteHeaderContents(XmlDictionaryWriter writer, MessageVersion messageVersion)
    {
        foreach (XmlNode child in element.ChildNodes)
        {
            child.WriteTo(writer);
        }
    }
}
