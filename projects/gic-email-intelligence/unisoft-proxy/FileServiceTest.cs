// Probe the Unisoft file service — try different WCF bindings.
// Compile: csc.exe /out:FileServiceTest.exe /reference:System.ServiceModel.dll /reference:System.Runtime.Serialization.dll /reference:System.Xml.dll FileServiceTest.cs

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

    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

[ServiceContract(Namespace = "http://tempuri.org/")]
interface IINSFileService
{
    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

class FileServiceTest
{
    static string soapUrl = "https://services.uat.gicunderwriters.co/management/imsservice.svc";
    static string fileUrl = "https://services.uat.gicunderwriters.co/attachments/insfileservice.svc";
    static string wsUser = "UniClient";
    static string wsPass = "J5j!}7=r/z";
    static string clientId = "GIC_UAT";

    static void Main()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        ServicePointManager.ServerCertificateValidationCallback =
            delegate(object s, X509Certificate c, X509Chain ch, SslPolicyErrors e) { return true; };

        Console.WriteLine("=== Unisoft File Service Probe ===");

        // Step 1: Get token from main service (exact same format as proxy)
        Console.WriteLine("\n1. Getting token from IIMSService...");
        string token = GetToken();
        if (token == null) { Console.WriteLine("   FAILED"); return; }
        Console.WriteLine("   Got token: " + token.Substring(0, Math.Min(20, token.Length)) + "...");

        // Step 2: Try file service with WSHttpBinding (same as main service)
        Console.WriteLine("\n2. WSHttpBinding + WS-Security...");
        TryFileService("WSHttp", CreateWSHttp(), true, token);

        // Step 3: Try BasicHttpBinding with transport security only
        Console.WriteLine("\n3. BasicHttpBinding + Transport...");
        TryFileService("BasicHttp", CreateBasicHttp(), false, token);

        // Step 4: Try BasicHttpBinding with MTOM encoding
        Console.WriteLine("\n4. BasicHttpBinding + MTOM...");
        TryFileService("BasicMtom", CreateBasicMtom(), false, token);

        // Step 5: Try WSHttpBinding without ReliableSession
        Console.WriteLine("\n5. WSHttpBinding - no ReliableSession...");
        TryFileService("WSHttp-noRS", CreateWSHttpNoRS(), true, token);
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
                "<Version i:nil=\"true\" xmlns=\"\"/>" +
                "</request>";

            string body = "<GetToken xmlns=\"http://tempuri.org/\">" + xml + "</GetToken>";
            Message req = Message.CreateMessage(
                MessageVersion.Soap12WSAddressing10,
                "http://tempuri.org/IIMSService/GetToken",
                XmlReader.Create(new StringReader(body)));
            Message resp = ch.GetToken(req);
            string respBody = ReadBody(resp);
            // Token is inside <AccessToken xmlns="">...</AccessToken>
            string search = "<AccessToken xmlns=\"\">";
            int s = respBody.IndexOf(search);
            if (s >= 0)
            {
                s += search.Length;
                int e = respBody.IndexOf("</AccessToken>", s);
                if (e > s) return respBody.Substring(s, e - s);
            }
            // Fallback: try without namespace
            search = "<AccessToken>";
            s = respBody.IndexOf(search);
            if (s >= 0)
            {
                s += search.Length;
                int e = respBody.IndexOf("</AccessToken>", s);
                if (e > s) return respBody.Substring(s, e - s);
            }
            Console.WriteLine("   Body: " + respBody.Substring(0, Math.Min(500, respBody.Length)));
            return null;
        }
        catch (Exception ex)
        {
            Console.WriteLine("   Error: " + ex.Message);
            if (ex.InnerException != null) Console.WriteLine("   Inner: " + ex.InnerException.Message);
            return null;
        }
        finally
        {
            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            f.Close();
        }
    }

    static void TryFileService(string label, Binding binding, bool useWsCredentials, string token)
    {
        try
        {
            ChannelFactory<IINSFileService> f;
            if (useWsCredentials)
            {
                f = new ChannelFactory<IINSFileService>(binding, new EndpointAddress(fileUrl));
                f.Credentials.UserName.UserName = wsUser;
                f.Credentials.UserName.Password = wsPass;
            }
            else
            {
                f = new ChannelFactory<IINSFileService>(binding, new EndpointAddress(fileUrl));
            }

            IINSFileService ch = f.CreateChannel();
            ((IClientChannel)ch).Open();

            // Try GetSupportedAttachmentTypes
            string reqXml = "<GetSupportedAttachmentTypes xmlns=\"http://tempuri.org/\">" +
                "<AccessToken>" + token + "</AccessToken>" +
                "</GetSupportedAttachmentTypes>";

            MessageVersion ver = MessageVersion.Soap12WSAddressing10;
            if (binding is BasicHttpBinding) ver = MessageVersion.Soap11;

            Message req = Message.CreateMessage(ver,
                "http://tempuri.org/IINSFileService/GetSupportedAttachmentTypes",
                XmlReader.Create(new StringReader(reqXml)));
            Message resp = ch.ProcessMessage(req);
            string body = ReadBody(resp);
            Console.WriteLine("   SUCCESS! Response (" + body.Length + " chars):");
            Console.WriteLine("   " + body.Substring(0, Math.Min(500, body.Length)));

            try { ((IClientChannel)ch).Close(); } catch { ((IClientChannel)ch).Abort(); }
            f.Close();
        }
        catch (Exception ex)
        {
            Console.WriteLine("   FAILED: " + ex.GetType().Name + ": " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("   Inner: " + ex.InnerException.GetType().Name + ": " + ex.InnerException.Message);
        }
    }

    static WSHttpBinding CreateWSHttp()
    {
        WSHttpBinding b = new WSHttpBinding();
        b.Security.Mode = SecurityMode.TransportWithMessageCredential;
        b.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
        b.Security.Message.EstablishSecurityContext = true;
        b.ReliableSession.Enabled = true;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        return b;
    }

    static WSHttpBinding CreateWSHttpNoRS()
    {
        WSHttpBinding b = new WSHttpBinding();
        b.Security.Mode = SecurityMode.TransportWithMessageCredential;
        b.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
        b.Security.Message.EstablishSecurityContext = true;
        b.ReliableSession.Enabled = false;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        return b;
    }

    static BasicHttpBinding CreateBasicHttp()
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        return b;
    }

    static BasicHttpBinding CreateBasicMtom()
    {
        BasicHttpBinding b = new BasicHttpBinding();
        b.Security.Mode = BasicHttpSecurityMode.Transport;
        b.MessageEncoding = WSMessageEncoding.Mtom;
        b.MaxReceivedMessageSize = 50 * 1024 * 1024;
        return b;
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
}
