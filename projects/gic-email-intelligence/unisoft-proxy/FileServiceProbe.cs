// Probe the file service API to understand AddQuoteAttachment format.
// Compile: csc.exe /out:FileServiceProbe.exe /reference:System.ServiceModel.dll /reference:System.Runtime.Serialization.dll /reference:System.Xml.dll FileServiceProbe.cs

using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
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

class FileServiceProbe
{
    static string soapUrl = "https://services.uat.gicunderwriters.co/management/imsservice.svc";
    static string fileUrl = "https://services.uat.gicunderwriters.co/attachments/insfileservice.svc";
    static string wsUser = "UniClient";
    static string wsPass = "J5j!}7=r/z";
    static string clientId = "GIC_UAT";

    static IINSFileService fileChannel;
    static ChannelFactory<IINSFileService> fileFactory;

    static void Main()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        ServicePointManager.ServerCertificateValidationCallback =
            delegate { return true; };

        Console.WriteLine("=== File Service Probe ===");

        // Get token
        string token = GetToken();
        if (token == null) { Console.WriteLine("FAILED to get token"); return; }
        Console.WriteLine("Token: " + token.Substring(0, 8) + "...");

        // Open file channel
        OpenFileChannel();

        // 1. Get attachment categories
        Console.WriteLine("\n=== GetAttachmentCategories ===");
        CallFile("GetAttachmentCategories",
            "<AccessToken>" + token + "</AccessToken>");

        // 2. Get supported types (already know this works)
        Console.WriteLine("\n=== GetSupportedAttachmentTypes ===");
        CallFile("GetSupportedAttachmentTypes",
            "<AccessToken>" + token + "</AccessToken>");

        // 3. Get attachments for a known quote (Quote 17140 from automation test)
        Console.WriteLine("\n=== GetQuoteAttachments (QuoteID=17140) ===");
        CallFile("GetQuoteAttachments",
            "<AccessToken>" + token + "</AccessToken>" +
            "<QuoteID>17140</QuoteID>");

        // 4. Try a test upload with a tiny PDF
        Console.WriteLine("\n=== AddQuoteAttachment (test) ===");
        // Create minimal test content
        byte[] testBytes = Encoding.UTF8.GetBytes("test attachment content");
        string base64 = Convert.ToBase64String(testBytes);
        CallFile("AddQuoteAttachment",
            "<AccessToken>" + token + "</AccessToken>" +
            "<QuoteID>17140</QuoteID>" +
            "<FileName>test-upload.txt</FileName>" +
            "<FileType>TXT</FileType>" +
            "<FileContent>" + base64 + "</FileContent>" +
            "<Category>Application</Category>" +
            "<Description>Test upload from probe</Description>" +
            "<UploadedBy>ccerto</UploadedBy>");

        // 5. Try with different parameter names (case sensitivity matters)
        Console.WriteLine("\n=== AddQuoteAttachment (alt params) ===");
        CallFile("AddQuoteAttachment",
            "<AccessToken>" + token + "</AccessToken>" +
            "<QuoteId>17140</QuoteId>" +
            "<Attachment xmlns:i=\"http://www.w3.org/2001/XMLSchema-instance\">" +
            "<FileName xmlns=\"\">test-upload2.txt</FileName>" +
            "<FileType xmlns=\"\">TXT</FileType>" +
            "<FileContent xmlns=\"\">" + base64 + "</FileContent>" +
            "<Category xmlns=\"\">Application</Category>" +
            "<Description xmlns=\"\">Test upload v2</Description>" +
            "<UploadedBy xmlns=\"\">ccerto</UploadedBy>" +
            "</Attachment>");

        CloseFileChannel();
    }

    static void CallFile(string op, string innerXml)
    {
        try
        {
            string body = "<" + op + " xmlns=\"http://tempuri.org/\">" + innerXml + "</" + op + ">";
            Message req = Message.CreateMessage(
                MessageVersion.Soap11,
                "http://tempuri.org/IINSFileService/" + op,
                XmlReader.Create(new StringReader(body)));
            Message resp = fileChannel.ProcessMessage(req);
            string respBody = ReadBody(resp);
            // Truncate for display
            if (respBody.Length > 1500)
                Console.WriteLine(respBody.Substring(0, 1500) + "\n... (" + respBody.Length + " total)");
            else
                Console.WriteLine(respBody);
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.GetType().Name + ": " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("  Inner: " + ex.InnerException.Message);
            // Reopen channel if faulted
            try
            {
                CloseFileChannel();
                OpenFileChannel();
            }
            catch { }
        }
    }

    static void OpenFileChannel()
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MessageEncoding = WSMessageEncoding.Mtom;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        b.SendTimeout = TimeSpan.FromSeconds(60);
        fileFactory = new ChannelFactory<IINSFileService>(b, new EndpointAddress(fileUrl));
        fileChannel = fileFactory.CreateChannel();
        ((IClientChannel)fileChannel).Open();
    }

    static void CloseFileChannel()
    {
        try { ((IClientChannel)fileChannel).Close(); } catch { ((IClientChannel)fileChannel).Abort(); }
        try { fileFactory.Close(); } catch { }
    }

    static string GetToken()
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
        XmlWriterSettings ws = new XmlWriterSettings();
        ws.Indent = false;
        using (XmlWriter w = XmlWriter.Create(sb, ws)) { msg.WriteBody(w); w.Flush(); }
        return sb.ToString();
    }
}
