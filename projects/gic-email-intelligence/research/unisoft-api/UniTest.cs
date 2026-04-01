using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Xml;

// Minimal service contract — just the operations we need to test
[ServiceContract(Namespace = "http://tempuri.org/")]
interface IIMSService
{
    [OperationContract(Action = "http://tempuri.org/IIMSService/GetToken",
                       ReplyAction = "http://tempuri.org/IIMSService/GetTokenResponse")]
    Message GetToken(Message request);

    [OperationContract(Action = "http://tempuri.org/IIMSService/GetInsuranceLOBs",
                       ReplyAction = "http://tempuri.org/IIMSService/GetInsuranceLOBsResponse")]
    Message GetInsuranceLOBs(Message request);

    [OperationContract(Action = "http://tempuri.org/IIMSService/GetInsuranceCarriers",
                       ReplyAction = "http://tempuri.org/IIMSService/GetInsuranceCarriersResponse")]
    Message GetInsuranceCarriers(Message request);

    [OperationContract(Action = "http://tempuri.org/IIMSService/GetQuote",
                       ReplyAction = "http://tempuri.org/IIMSService/GetQuoteResponse")]
    Message GetQuote(Message request);
}

class UniTest
{
    static void Main(string[] args)
    {
        string op = args.Length > 0 ? args[0] : "GetInsuranceLOBs";

        // Enable TLS 1.2 and accept UAT certificates
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        ServicePointManager.ServerCertificateValidationCallback =
            delegate(object s, X509Certificate cert, X509Chain chain, SslPolicyErrors errors) { return true; };

        Console.WriteLine("=== Unisoft WCF Client Test ===");
        Console.WriteLine("Operation: " + op);
        Console.WriteLine();

        try
        {
            // Configure wsHttpBinding to match the server's security policy
            var binding = new WSHttpBinding();
            binding.Security.Mode = SecurityMode.TransportWithMessageCredential;
            binding.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
            binding.Security.Message.EstablishSecurityContext = true;
            binding.ReliableSession.Enabled = true;

            // Increase timeouts and message sizes for large responses
            binding.MaxReceivedMessageSize = 10 * 1024 * 1024; // 10MB
            binding.ReaderQuotas.MaxStringContentLength = 10 * 1024 * 1024;
            binding.OpenTimeout = TimeSpan.FromSeconds(30);
            binding.SendTimeout = TimeSpan.FromSeconds(60);
            binding.ReceiveTimeout = TimeSpan.FromSeconds(60);

            var endpoint = new EndpointAddress(
                "https://services.uat.gicunderwriters.co/management/imsservice.svc");

            var factory = new ChannelFactory<IIMSService>(binding, endpoint);

            // WS-Security UsernameToken credentials
            factory.Credentials.UserName.UserName = "UniClient";
            factory.Credentials.UserName.Password = "J5j!}7=r/z";

            Console.WriteLine("Creating channel...");
            var channel = factory.CreateChannel();
            ((IClientChannel)channel).Open();
            Console.WriteLine("Channel opened successfully!");
            Console.WriteLine();

            // Step 1: Always get token first
            Console.WriteLine("Step 1: Getting access token...");
            string tokenResponse = CallGetToken(channel);
            string accessToken = ExtractAccessToken(tokenResponse);
            Console.WriteLine("Access Token: " + accessToken);
            Console.WriteLine();

            string response = null;

            switch (op)
            {
                case "GetInsuranceLOBs":
                    response = CallGetInsuranceLOBs(channel, accessToken);
                    break;
                case "GetInsuranceCarriers":
                    response = CallGetInsuranceCarriers(channel, accessToken);
                    break;
                case "GetToken":
                    response = tokenResponse; // Already called above
                    break;
                case "GetQuote":
                    string quoteId = args.Length > 1 ? args[1] : "17129";
                    response = CallGetQuote(channel, quoteId);
                    break;
                default:
                    Console.WriteLine("Unknown operation: " + op);
                    break;
            }

            if (response != null)
            {
                Console.WriteLine("=== RESPONSE ===");
                Console.WriteLine(response);
            }

            ((IClientChannel)channel).Close();
            factory.Close();
            Console.WriteLine();
            Console.WriteLine("=== SUCCESS ===");
        }
        catch (FaultException ex)
        {
            Console.WriteLine("SOAP FAULT: " + ex.Message);
            Console.WriteLine("Detail: " + ex.ToString());
        }
        catch (CommunicationException ex)
        {
            Console.WriteLine("COMMUNICATION ERROR: " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("Inner: " + ex.InnerException.Message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.GetType().Name + ": " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("Inner: " + ex.InnerException.Message);
            Console.WriteLine(ex.StackTrace);
        }
    }

    static string CallGetInsuranceLOBs(IIMSService channel, string accessToken)
    {
        Console.WriteLine("Calling GetInsuranceLOBs...");
        string body = @"<GetInsuranceLOBs xmlns=""http://tempuri.org/"">
            <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                <ClientId xmlns="""">GIC_UAT</ClientId>
                <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                <IsDeveloper xmlns="""">false</IsDeveloper>
                <RequestId xmlns="""">" + Guid.NewGuid().ToString() + @"</RequestId>
                <RequestedByUserName i:nil=""true"" xmlns=""""/>
                <Version i:nil=""true"" xmlns=""""/>
                <SortExpression xmlns=""""/>
            </request>
        </GetInsuranceLOBs>";
        var reader = XmlReader.Create(new StringReader(body));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/GetInsuranceLOBs",
            reader);
        var result = channel.GetInsuranceLOBs(msg);
        return MessageToString(result);
    }

    static string CallGetInsuranceCarriers(IIMSService channel, string accessToken)
    {
        Console.WriteLine("Calling GetInsuranceCarriers...");
        string body = @"<GetInsuranceCarriers xmlns=""http://tempuri.org/"">
            <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                <ClientId xmlns="""">GIC_UAT</ClientId>
                <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                <IsDeveloper xmlns="""">false</IsDeveloper>
                <RequestId xmlns="""">" + Guid.NewGuid().ToString() + @"</RequestId>
                <RequestedByUserName i:nil=""true"" xmlns=""""/>
                <Version i:nil=""true"" xmlns=""""/>
            </request>
        </GetInsuranceCarriers>";
        var reader = XmlReader.Create(new StringReader(body));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/GetInsuranceCarriers",
            reader);
        var result = channel.GetInsuranceCarriers(msg);
        return MessageToString(result);
    }

    static string CallGetToken(IIMSService channel)
    {
        Console.WriteLine("Calling GetToken...");

        // Build the GetToken request body
        string body = @"<GetToken xmlns=""http://tempuri.org/"">
            <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                <AccessToken i:nil=""true"" xmlns=""""/>
                <ClientId xmlns="""">GIC_UAT</ClientId>
                <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                <IsDeveloper xmlns="""">false</IsDeveloper>
                <RequestId xmlns="""">00000000-0000-0000-0000-000000000001</RequestId>
                <RequestedByUserName i:nil=""true"" xmlns=""""/>
                <Version i:nil=""true"" xmlns=""""/>
            </request>
        </GetToken>";

        var reader = XmlReader.Create(new StringReader(body));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/GetToken",
            reader);
        var result = channel.GetToken(msg);
        return MessageToString(result);
    }

    static string CallGetQuote(IIMSService channel, string quoteId)
    {
        Console.WriteLine("Calling GetQuote for QuoteId=" + quoteId + "...");

        string body = @"<GetQuote xmlns=""http://tempuri.org/"">
            <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                <AccessToken xmlns="""">placeholder</AccessToken>
                <QuoteId xmlns="""">" + quoteId + @"</QuoteId>
            </request>
        </GetQuote>";

        var reader = XmlReader.Create(new StringReader(body));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/GetQuote",
            reader);
        var result = channel.GetQuote(msg);
        return MessageToString(result);
    }

    static string ExtractAccessToken(string xml)
    {
        // Parse XML to find <AccessToken>...</AccessToken>
        try
        {
            int start = xml.IndexOf("<AccessToken");
            if (start < 0) return "TOKEN_NOT_FOUND";
            start = xml.IndexOf(">", start) + 1;
            int end = xml.IndexOf("</AccessToken>", start);
            if (end < 0) return "TOKEN_NOT_FOUND";
            return xml.Substring(start, end - start);
        }
        catch
        {
            return "TOKEN_PARSE_ERROR";
        }
    }

    static string MessageToString(Message msg)
    {
        using (var sw = new StringWriter())
        using (var writer = XmlWriter.Create(sw, new XmlWriterSettings { Indent = true }))
        {
            msg.WriteBody(writer);
            writer.Flush();
            return sw.ToString();
        }
    }
}

