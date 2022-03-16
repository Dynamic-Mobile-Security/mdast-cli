"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10googleplay.proto\"\xe6\x03\n\x16\x41ndroidAppDeliveryData\x12\x14\n\x0c\x64ownloadSize\x18\x01 \x01(\x03\x12\x0c\n\x04sha1\x18\x02 \x01(\t\x12\x13\n\x0b\x64ownloadUrl\x18\x03 \x01(\t\x12(\n\x0e\x61\x64\x64itionalFile\x18\x04 \x03(\x0b\x32\x10.AppFileMetadata\x12\'\n\x12\x64ownloadAuthCookie\x18\x05 \x03(\x0b\x32\x0b.HttpCookie\x12\x15\n\rforwardLocked\x18\x06 \x01(\x08\x12\x15\n\rrefundTimeout\x18\x07 \x01(\x03\x12\x17\n\x0fserverInitiated\x18\x08 \x01(\x08\x12%\n\x1dpostInstallRefundWindowMillis\x18\t \x01(\x03\x12\x1c\n\x14immediateStartNeeded\x18\n \x01(\x08\x12\'\n\tpatchData\x18\x0b \x01(\x0b\x32\x14.AndroidAppPatchData\x12+\n\x10\x65ncryptionParams\x18\x0c \x01(\x0b\x32\x11.EncryptionParams\x12\x1a\n\x12\x64ownloadUrlGzipped\x18\r \x01(\t\x12\x1b\n\x13\x64ownloadSizeGzipped\x18\x0e \x01(\x03\x12\x15\n\x05split\x18\x0f \x03(\x0b\x32\x06.Split\x12\x0e\n\x06sha256\x18\x13 \x01(\t\"\x87\x01\n\x05Split\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x03\x12\x13\n\x0bsizeGzipped\x18\x03 \x01(\x03\x12\x0c\n\x04sha1\x18\x04 \x01(\t\x12\x13\n\x0b\x64ownloadUrl\x18\x05 \x01(\t\x12\x1a\n\x12\x64ownloadUrlGzipped\x18\x06 \x01(\t\x12\x0e\n\x06sha256\x18\t \x01(\t\"\x80\x01\n\x13\x41ndroidAppPatchData\x12\x17\n\x0f\x62\x61seVersionCode\x18\x01 \x01(\x05\x12\x10\n\x08\x62\x61seSha1\x18\x02 \x01(\t\x12\x13\n\x0b\x64ownloadUrl\x18\x03 \x01(\t\x12\x13\n\x0bpatchFormat\x18\x04 \x01(\x05\x12\x14\n\x0cmaxPatchSize\x18\x05 \x01(\x03\"\x9a\x01\n\x0f\x41ppFileMetadata\x12\x10\n\x08\x66ileType\x18\x01 \x01(\x05\x12\x13\n\x0bversionCode\x18\x02 \x01(\x05\x12\x0c\n\x04size\x18\x03 \x01(\x03\x12\x13\n\x0b\x64ownloadUrl\x18\x04 \x01(\t\x12\x13\n\x0bsizeGzipped\x18\x06 \x01(\x03\x12\x1a\n\x12\x64ownloadUrlGzipped\x18\x07 \x01(\t\x12\x0c\n\x04sha1\x18\x08 \x01(\t\"K\n\x10\x45ncryptionParams\x12\x0f\n\x07version\x18\x01 \x01(\x05\x12\x15\n\rencryptionKey\x18\x02 \x01(\t\x12\x0f\n\x07hmacKey\x18\x03 \x01(\t\")\n\nHttpCookie\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"\xad\x02\n\x07\x41\x64\x64ress\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0c\x61\x64\x64ressLine1\x18\x02 \x01(\t\x12\x14\n\x0c\x61\x64\x64ressLine2\x18\x03 \x01(\t\x12\x0c\n\x04\x63ity\x18\x04 \x01(\t\x12\r\n\x05state\x18\x05 \x01(\t\x12\x12\n\npostalCode\x18\x06 \x01(\t\x12\x15\n\rpostalCountry\x18\x07 \x01(\t\x12\x19\n\x11\x64\x65pendentLocality\x18\x08 \x01(\t\x12\x13\n\x0bsortingCode\x18\t \x01(\t\x12\x14\n\x0clanguageCode\x18\n \x01(\t\x12\x13\n\x0bphoneNumber\x18\x0b \x01(\t\x12\x11\n\tisReduced\x18\x0c \x01(\x08\x12\x11\n\tfirstName\x18\r \x01(\t\x12\x10\n\x08lastName\x18\x0e \x01(\t\x12\r\n\x05\x65mail\x18\x0f \x01(\t\"J\n\nBookAuthor\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x17\n\x0f\x64\x65precatedQuery\x18\x02 \x01(\t\x12\x15\n\x05\x64ocid\x18\x03 \x01(\x0b\x32\x06.Docid\"\xc3\x03\n\x0b\x42ookDetails\x12\x1d\n\x07subject\x18\x03 \x03(\x0b\x32\x0c.BookSubject\x12\x11\n\tpublisher\x18\x04 \x01(\t\x12\x17\n\x0fpublicationDate\x18\x05 \x01(\t\x12\x0c\n\x04isbn\x18\x06 \x01(\t\x12\x15\n\rnumberOfPages\x18\x07 \x01(\x05\x12\x10\n\x08subtitle\x18\x08 \x01(\t\x12\x1b\n\x06\x61uthor\x18\t \x03(\x0b\x32\x0b.BookAuthor\x12\x11\n\treaderUrl\x18\n \x01(\t\x12\x17\n\x0f\x64ownloadEpubUrl\x18\x0b \x01(\t\x12\x16\n\x0e\x64ownloadPdfUrl\x18\x0c \x01(\t\x12\x17\n\x0f\x61\x63sEpubTokenUrl\x18\r \x01(\t\x12\x16\n\x0e\x61\x63sPdfTokenUrl\x18\x0e \x01(\t\x12\x15\n\repubAvailable\x18\x0f \x01(\x08\x12\x14\n\x0cpdfAvailable\x18\x10 \x01(\x08\x12\x16\n\x0e\x61\x62outTheAuthor\x18\x11 \x01(\t\x12+\n\nidentifier\x18\x12 \x03(\n2\x17.BookDetails.Identifier\x1a.\n\nIdentifier\x12\x0c\n\x04type\x18\x13 \x01(\x05\x12\x12\n\nidentifier\x18\x14 \x01(\t\"=\n\x0b\x42ookSubject\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05query\x18\x02 \x01(\t\x12\x11\n\tsubjectId\x18\x03 \x01(\t\"~\n\nBrowseLink\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x64\x61taUrl\x18\x03 \x01(\t\x12\x14\n\x04icon\x18\x05 \x01(\x0b\x32\x06.Image\x12;\n\x18unknownCategoryContainer\x18\x04 \x01(\x0b\x32\x19.UnknownCategoryContainer\"M\n\x18UnknownCategoryContainer\x12\x31\n\x13\x63\x61tegoryIdContainer\x18\x05 \x01(\x0b\x32\x14.CategoryIdContainer\")\n\x13\x43\x61tegoryIdContainer\x12\x12\n\ncategoryId\x18\x04 \x01(\t\"\xa6\x01\n\x0e\x42rowseResponse\x12\x13\n\x0b\x63ontentsUrl\x18\x01 \x01(\t\x12\x10\n\x08promoUrl\x18\x02 \x01(\t\x12\x1d\n\x08\x63\x61tegory\x18\x03 \x03(\x0b\x32\x0b.BrowseLink\x12\x1f\n\nbreadcrumb\x18\x04 \x03(\x0b\x32\x0b.BrowseLink\x12-\n\x11\x63\x61tegoryContainer\x18\t \x01(\x0b\x32\x12.CategoryContainer\"2\n\x11\x43\x61tegoryContainer\x12\x1d\n\x08\x63\x61tegory\x18\x04 \x03(\x0b\x32\x0b.BrowseLink\"\x8f\x02\n\x10\x41\x64\x64ressChallenge\x12\x1c\n\x14responseAddressParam\x18\x01 \x01(\t\x12\x1f\n\x17responseCheckboxesParam\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x17\n\x0f\x64\x65scriptionHtml\x18\x04 \x01(\t\x12\x1f\n\x08\x63heckbox\x18\x05 \x03(\x0b\x32\r.FormCheckbox\x12\x19\n\x07\x61\x64\x64ress\x18\x06 \x01(\x0b\x32\x08.Address\x12.\n\x0f\x65rrorInputField\x18\x07 \x03(\x0b\x32\x15.InputValidationError\x12\x11\n\terrorHtml\x18\x08 \x01(\t\x12\x15\n\rrequiredField\x18\t \x03(\x05\"\xef\x01\n\x17\x41uthenticationChallenge\x12\x1a\n\x12\x61uthenticationType\x18\x01 \x01(\x05\x12\'\n\x1fresponseAuthenticationTypeParam\x18\x02 \x01(\t\x12\x1f\n\x17responseRetryCountParam\x18\x03 \x01(\t\x12\x15\n\rpinHeaderText\x18\x04 \x01(\t\x12\x1e\n\x16pinDescriptionTextHtml\x18\x05 \x01(\t\x12\x16\n\x0egaiaHeaderText\x18\x06 \x01(\t\x12\x1f\n\x17gaiaDescriptionTextHtml\x18\x07 \x01(\t\"\x98\t\n\x0b\x42uyResponse\x12\x37\n\x10purchaseResponse\x18\x01 \x01(\x0b\x32\x1d.PurchaseNotificationResponse\x12/\n\x0c\x63heckoutinfo\x18\x02 \x01(\n2\x19.BuyResponse.CheckoutInfo\x12\x16\n\x0e\x63ontinueViaUrl\x18\x08 \x01(\t\x12\x19\n\x11purchaseStatusUrl\x18\t \x01(\t\x12\x19\n\x11\x63heckoutServiceId\x18\x0c \x01(\t\x12\x1d\n\x15\x63heckoutTokenRequired\x18\r \x01(\x08\x12\x17\n\x0f\x62\x61seCheckoutUrl\x18\x0e \x01(\t\x12\x17\n\x0ftosCheckboxHtml\x18% \x03(\t\x12\x1a\n\x12iabPermissionError\x18& \x01(\x05\x12\x37\n\x16purchaseStatusResponse\x18\' \x01(\x0b\x32\x17.PurchaseStatusResponse\x12\x16\n\x0epurchaseCookie\x18. \x01(\t\x12\x1d\n\tchallenge\x18\x31 \x01(\x0b\x32\n.Challenge\x12\x15\n\rdownloadToken\x18\x37 \x01(\t\x1a\xdc\x05\n\x0c\x43heckoutInfo\x12\x17\n\x04item\x18\x03 \x01(\x0b\x32\t.LineItem\x12\x1a\n\x07subItem\x18\x04 \x03(\x0b\x32\t.LineItem\x12@\n\x0e\x63heckoutoption\x18\x05 \x03(\n2(.BuyResponse.CheckoutInfo.CheckoutOption\x12\x1d\n\x15\x64\x65precatedCheckoutUrl\x18\n \x01(\t\x12\x18\n\x10\x61\x64\x64InstrumentUrl\x18\x0b \x01(\t\x12\x12\n\nfooterHtml\x18\x14 \x03(\t\x12 \n\x18\x65ligibleInstrumentFamily\x18\x1f \x03(\x05\x12\x14\n\x0c\x66ootnoteHtml\x18$ \x03(\t\x12\'\n\x12\x65ligibleInstrument\x18, \x03(\x0b\x32\x0b.Instrument\x1a\xa6\x03\n\x0e\x43heckoutOption\x12\x15\n\rformOfPayment\x18\x06 \x01(\t\x12\x1b\n\x13\x65ncodedAdjustedCart\x18\x07 \x01(\t\x12\x14\n\x0cinstrumentId\x18\x0f \x01(\t\x12\x17\n\x04item\x18\x10 \x03(\x0b\x32\t.LineItem\x12\x1a\n\x07subItem\x18\x11 \x03(\x0b\x32\t.LineItem\x12\x18\n\x05total\x18\x12 \x01(\x0b\x32\t.LineItem\x12\x12\n\nfooterHtml\x18\x13 \x03(\t\x12\x18\n\x10instrumentFamily\x18\x1d \x01(\x05\x12.\n&deprecatedInstrumentInapplicableReason\x18\x1e \x03(\x05\x12\x1a\n\x12selectedInstrument\x18  \x01(\x08\x12\x1a\n\x07summary\x18! \x01(\x0b\x32\t.LineItem\x12\x14\n\x0c\x66ootnoteHtml\x18# \x03(\t\x12\x1f\n\ninstrument\x18+ \x01(\x0b\x32\x0b.Instrument\x12\x16\n\x0epurchaseCookie\x18- \x01(\t\x12\x16\n\x0e\x64isabledReason\x18\x30 \x03(\t\"s\n\tChallenge\x12+\n\x10\x61\x64\x64ressChallenge\x18\x01 \x01(\x0b\x32\x11.AddressChallenge\x12\x39\n\x17\x61uthenticationChallenge\x18\x02 \x01(\x0b\x32\x18.AuthenticationChallenge\"F\n\x0c\x46ormCheckbox\x12\x13\n\x0b\x64\x65scription\x18\x01 \x01(\t\x12\x0f\n\x07\x63hecked\x18\x02 \x01(\x08\x12\x10\n\x08required\x18\x03 \x01(\x08\"\\\n\x08LineItem\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x15\n\x05offer\x18\x03 \x01(\x0b\x32\x06.Offer\x12\x16\n\x06\x61mount\x18\x04 \x01(\x0b\x32\x06.Money\"F\n\x05Money\x12\x0e\n\x06micros\x18\x01 \x01(\x03\x12\x14\n\x0c\x63urrencyCode\x18\x02 \x01(\t\x12\x17\n\x0f\x66ormattedAmount\x18\x03 \x01(\t\"\x80\x01\n\x1cPurchaseNotificationResponse\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x1d\n\tdebugInfo\x18\x02 \x01(\x0b\x32\n.DebugInfo\x12\x1d\n\x15localizedErrorMessage\x18\x03 \x01(\t\x12\x12\n\npurchaseId\x18\x04 \x01(\t\"\xf9\x01\n\x16PurchaseStatusResponse\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x11\n\tstatusMsg\x18\x02 \x01(\t\x12\x13\n\x0bstatusTitle\x18\x03 \x01(\t\x12\x14\n\x0c\x62riefMessage\x18\x04 \x01(\t\x12\x0f\n\x07infoUrl\x18\x05 \x01(\t\x12%\n\rlibraryUpdate\x18\x06 \x01(\x0b\x32\x0e.LibraryUpdate\x12\'\n\x12rejectedInstrument\x18\x07 \x01(\x0b\x32\x0b.Instrument\x12\x30\n\x0f\x61ppDeliveryData\x18\x08 \x01(\x0b\x32\x17.AndroidAppDeliveryData\"D\n\x10\x44\x65liveryResponse\x12\x30\n\x0f\x61ppDeliveryData\x18\x02 \x01(\x0b\x32\x17.AndroidAppDeliveryData\"<\n\x05\x44ocid\x12\x14\n\x0c\x62\x61\x63kendDocid\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\x05\x12\x0f\n\x07\x62\x61\x63kend\x18\x03 \x01(\x05\">\n\x07Install\x12\x11\n\tandroidId\x18\x01 \x01(\x06\x12\x0f\n\x07version\x18\x02 \x01(\x05\x12\x0f\n\x07\x62undled\x18\x03 \x01(\x08\"\xce\x03\n\x05Offer\x12\x0e\n\x06micros\x18\x01 \x01(\x03\x12\x14\n\x0c\x63urrencyCode\x18\x02 \x01(\t\x12\x17\n\x0f\x66ormattedAmount\x18\x03 \x01(\t\x12\x1e\n\x0e\x63onvertedPrice\x18\x04 \x03(\x0b\x32\x06.Offer\x12\x1c\n\x14\x63heckoutFlowRequired\x18\x05 \x01(\x08\x12\x17\n\x0f\x66ullPriceMicros\x18\x06 \x01(\x03\x12\x1b\n\x13\x66ormattedFullAmount\x18\x07 \x01(\t\x12\x11\n\tofferType\x18\x08 \x01(\x05\x12!\n\x0brentalTerms\x18\t \x01(\x0b\x32\x0c.RentalTerms\x12\x12\n\nonSaleDate\x18\n \x01(\x03\x12\x16\n\x0epromotionLabel\x18\x0b \x03(\t\x12-\n\x11subscriptionTerms\x18\x0c \x01(\x0b\x32\x12.SubscriptionTerms\x12\x15\n\rformattedName\x18\r \x01(\t\x12\x1c\n\x14\x66ormattedDescription\x18\x0e \x01(\t\x12\x0c\n\x04sale\x18\x16 \x01(\x08\x12\x0f\n\x07message\x18\x1a \x01(\t\x12\x18\n\x10saleEndTimestamp\x18\x1e \x01(\x03\x12\x13\n\x0bsaleMessage\x18\x1f \x01(\t\"\xb1\x01\n\rOwnershipInfo\x12\x1f\n\x17initiationTimestampMsec\x18\x01 \x01(\x03\x12\x1f\n\x17validUntilTimestampMsec\x18\x02 \x01(\x03\x12\x14\n\x0c\x61utoRenewing\x18\x03 \x01(\x08\x12\"\n\x1arefundTimeoutTimestampMsec\x18\x04 \x01(\x03\x12$\n\x1cpostDeliveryRefundWindowMsec\x18\x05 \x01(\x03\"H\n\x0bRentalTerms\x12\x1a\n\x12grantPeriodSeconds\x18\x01 \x01(\x05\x12\x1d\n\x15\x61\x63tivatePeriodSeconds\x18\x02 \x01(\x05\"[\n\x11SubscriptionTerms\x12$\n\x0frecurringPeriod\x18\x01 \x01(\x0b\x32\x0b.TimePeriod\x12 \n\x0btrialPeriod\x18\x02 \x01(\x0b\x32\x0b.TimePeriod\")\n\nTimePeriod\x12\x0c\n\x04unit\x18\x01 \x01(\x05\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\"G\n\x12\x42illingAddressSpec\x12\x1a\n\x12\x62illingAddressType\x18\x01 \x01(\x05\x12\x15\n\rrequiredField\x18\x02 \x03(\x05\">\n\x19\x43\x61rrierBillingCredentials\x12\r\n\x05value\x18\x01 \x01(\t\x12\x12\n\nexpiration\x18\x02 \x01(\x03\"\xa9\x02\n\x18\x43\x61rrierBillingInstrument\x12\x15\n\rinstrumentKey\x18\x01 \x01(\t\x12\x13\n\x0b\x61\x63\x63ountType\x18\x02 \x01(\t\x12\x14\n\x0c\x63urrencyCode\x18\x03 \x01(\t\x12\x18\n\x10transactionLimit\x18\x04 \x01(\x03\x12\x1c\n\x14subscriberIdentifier\x18\x05 \x01(\t\x12\x39\n\x17\x65ncryptedSubscriberInfo\x18\x06 \x01(\x0b\x32\x18.EncryptedSubscriberInfo\x12/\n\x0b\x63redentials\x18\x07 \x01(\x0b\x32\x1a.CarrierBillingCredentials\x12\'\n\x12\x61\x63\x63\x65ptedCarrierTos\x18\x08 \x01(\x0b\x32\x0b.CarrierTos\"\xca\x01\n\x1e\x43\x61rrierBillingInstrumentStatus\x12\x1f\n\ncarrierTos\x18\x01 \x01(\x0b\x32\x0b.CarrierTos\x12\x1b\n\x13\x61ssociationRequired\x18\x02 \x01(\x08\x12\x18\n\x10passwordRequired\x18\x03 \x01(\x08\x12.\n\x15\x63\x61rrierPasswordPrompt\x18\x04 \x01(\x0b\x32\x0f.PasswordPrompt\x12\x12\n\napiVersion\x18\x05 \x01(\x05\x12\x0c\n\x04name\x18\x06 \x01(\t\"\x8e\x01\n\nCarrierTos\x12 \n\x06\x64\x63\x62Tos\x18\x01 \x01(\x0b\x32\x10.CarrierTosEntry\x12 \n\x06piiTos\x18\x02 \x01(\x0b\x32\x10.CarrierTosEntry\x12\x1d\n\x15needsDcbTosAcceptance\x18\x03 \x01(\x08\x12\x1d\n\x15needsPiiTosAcceptance\x18\x04 \x01(\x08\"/\n\x0f\x43\x61rrierTosEntry\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"\xa2\x01\n\x14\x43reditCardInstrument\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x14\n\x0c\x65scrowHandle\x18\x02 \x01(\t\x12\x12\n\nlastDigits\x18\x03 \x01(\t\x12\x17\n\x0f\x65xpirationMonth\x18\x04 \x01(\x05\x12\x16\n\x0e\x65xpirationYear\x18\x05 \x01(\x05\x12!\n\x0e\x65scrowEfeParam\x18\x06 \x03(\x0b\x32\t.EfeParam\"&\n\x08\x45\x66\x65Param\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t\"@\n\x14InputValidationError\x12\x12\n\ninputField\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\"\xc2\x02\n\nInstrument\x12\x14\n\x0cinstrumentId\x18\x01 \x01(\t\x12 \n\x0e\x62illingAddress\x18\x02 \x01(\x0b\x32\x08.Address\x12)\n\ncreditCard\x18\x03 \x01(\x0b\x32\x15.CreditCardInstrument\x12\x31\n\x0e\x63\x61rrierBilling\x18\x04 \x01(\x0b\x32\x19.CarrierBillingInstrument\x12/\n\x12\x62illingAddressSpec\x18\x05 \x01(\x0b\x32\x13.BillingAddressSpec\x12\x18\n\x10instrumentFamily\x18\x06 \x01(\x05\x12=\n\x14\x63\x61rrierBillingStatus\x18\x07 \x01(\x0b\x32\x1f.CarrierBillingInstrumentStatus\x12\x14\n\x0c\x64isplayTitle\x18\x08 \x01(\t\";\n\x0ePasswordPrompt\x12\x0e\n\x06prompt\x18\x01 \x01(\t\x12\x19\n\x11\x66orgotPasswordUrl\x18\x02 \x01(\t\"\x92\x01\n\x11\x43ontainerMetadata\x12\x11\n\tbrowseUrl\x18\x01 \x01(\t\x12\x13\n\x0bnextPageUrl\x18\x02 \x01(\t\x12\x11\n\trelevance\x18\x03 \x01(\x01\x12\x18\n\x10\x65stimatedResults\x18\x04 \x01(\x03\x12\x17\n\x0f\x61nalyticsCookie\x18\x05 \x01(\t\x12\x0f\n\x07ordered\x18\x06 \x01(\x08\"i\n\tDebugInfo\x12\x0f\n\x07message\x18\x01 \x03(\t\x12!\n\x06timing\x18\x02 \x03(\n2\x11.DebugInfo.Timing\x1a(\n\x06Timing\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x10\n\x08timeInMs\x18\x04 \x01(\x01\"\'\n\x10\x42ulkDetailsEntry\x12\x13\n\x03\x64oc\x18\x01 \x01(\x0b\x32\x06.DocV2\"=\n\x12\x42ulkDetailsRequest\x12\r\n\x05\x64ocid\x18\x01 \x03(\t\x12\x18\n\x10includeChildDocs\x18\x02 \x01(\x08\"7\n\x13\x42ulkDetailsResponse\x12 \n\x05\x65ntry\x18\x01 \x03(\x0b\x32\x11.BulkDetailsEntry\"\x93\x02\n\x0f\x44\x65tailsResponse\x12\x15\n\x05\x64ocV1\x18\x01 \x01(\x0b\x32\x06.DocV1\x12\x17\n\x0f\x61nalyticsCookie\x18\x02 \x01(\t\x12\x1b\n\nuserReview\x18\x03 \x01(\x0b\x32\x07.Review\x12\x15\n\x05\x64ocV2\x18\x04 \x01(\x0b\x32\x06.DocV2\x12\x12\n\nfooterHtml\x18\x05 \x01(\t\x12\x15\n\x05\x62\x61\x64ge\x18\x07 \x03(\x0b\x32\x06.Badge\x12\x1b\n\x08\x66\x65\x61tures\x18\x0c \x01(\x0b\x32\t.Features\x12\x18\n\x10\x64\x65tailsStreamUrl\x18\r \x01(\t\x12\x15\n\ruserReviewUrl\x18\x0e \x01(\t\x12#\n\x1bpostAcquireDetailsStreamUrl\x18\x11 \x01(\t\"i\n\x05\x42\x61\x64ge\x12\r\n\x05label\x18\x01 \x01(\t\x12\x15\n\x05image\x18\x02 \x01(\x0b\x32\x06.Image\x12)\n\x0f\x62\x61\x64geContainer1\x18\x04 \x01(\x0b\x32\x10.BadgeContainer1\x12\x0f\n\x07message\x18\x0b \x01(\t\"<\n\x0f\x42\x61\x64geContainer1\x12)\n\x0f\x62\x61\x64geContainer2\x18\x01 \x01(\x0b\x32\x10.BadgeContainer2\"B\n\x0f\x42\x61\x64geContainer2\x12/\n\x12\x62\x61\x64geLinkContainer\x18\x02 \x01(\x0b\x32\x13.BadgeLinkContainer\"\"\n\x12\x42\x61\x64geLinkContainer\x12\x0c\n\x04link\x18\x02 \x01(\t\"N\n\x08\x46\x65\x61tures\x12!\n\x0f\x66\x65\x61turePresence\x18\x01 \x03(\x0b\x32\x08.Feature\x12\x1f\n\rfeatureRating\x18\x02 \x03(\x0b\x32\x08.Feature\"\'\n\x07\x46\x65\x61ture\x12\r\n\x05label\x18\x01 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\"\xb5\x03\n\x18\x44\x65viceConfigurationProto\x12\x13\n\x0btouchScreen\x18\x01 \x01(\x05\x12\x10\n\x08keyboard\x18\x02 \x01(\x05\x12\x12\n\nnavigation\x18\x03 \x01(\x05\x12\x14\n\x0cscreenLayout\x18\x04 \x01(\x05\x12\x17\n\x0fhasHardKeyboard\x18\x05 \x01(\x08\x12\x1c\n\x14hasFiveWayNavigation\x18\x06 \x01(\x08\x12\x15\n\rscreenDensity\x18\x07 \x01(\x05\x12\x13\n\x0bglEsVersion\x18\x08 \x01(\x05\x12\x1b\n\x13systemSharedLibrary\x18\t \x03(\t\x12\x1e\n\x16systemAvailableFeature\x18\n \x03(\t\x12\x16\n\x0enativePlatform\x18\x0b \x03(\t\x12\x13\n\x0bscreenWidth\x18\x0c \x01(\x05\x12\x14\n\x0cscreenHeight\x18\r \x01(\x05\x12\x1d\n\x15systemSupportedLocale\x18\x0e \x03(\t\x12\x13\n\x0bglExtension\x18\x0f \x03(\t\x12\x13\n\x0b\x64\x65viceClass\x18\x10 \x01(\x05\x12\x1c\n\x14maxApkDownloadSizeMb\x18\x11 \x01(\x05\"\xff\x03\n\x08\x44ocument\x12\x15\n\x05\x64ocid\x18\x01 \x01(\x0b\x32\x06.Docid\x12\x1a\n\nfetchDocid\x18\x02 \x01(\x0b\x32\x06.Docid\x12\x1b\n\x0bsampleDocid\x18\x03 \x01(\x0b\x32\x06.Docid\x12\r\n\x05title\x18\x04 \x01(\t\x12\x0b\n\x03url\x18\x05 \x01(\t\x12\x0f\n\x07snippet\x18\x06 \x03(\t\x12\x1f\n\x0fpriceDeprecated\x18\x07 \x01(\x0b\x32\x06.Offer\x12#\n\x0c\x61vailability\x18\t \x01(\x0b\x32\r.Availability\x12\x15\n\x05image\x18\n \x03(\x0b\x32\x06.Image\x12\x18\n\x05\x63hild\x18\x0b \x03(\x0b\x32\t.Document\x12)\n\x0f\x61ggregateRating\x18\r \x01(\x0b\x32\x10.AggregateRating\x12\x15\n\x05offer\x18\x0e \x03(\x0b\x32\x06.Offer\x12*\n\x11translatedSnippet\x18\x0f \x03(\x0b\x32\x0f.TranslatedText\x12)\n\x0f\x64ocumentVariant\x18\x10 \x03(\x0b\x32\x10.DocumentVariant\x12\x12\n\ncategoryId\x18\x11 \x03(\t\x12\x1d\n\ndecoration\x18\x12 \x03(\x0b\x32\t.Document\x12\x19\n\x06parent\x18\x13 \x03(\x0b\x32\t.Document\x12\x18\n\x10privacyPolicyUrl\x18\x14 \x01(\t\"\x81\x02\n\x0f\x44ocumentVariant\x12\x15\n\rvariationType\x18\x01 \x01(\x05\x12\x13\n\x04rule\x18\x02 \x01(\x0b\x32\x05.Rule\x12\r\n\x05title\x18\x03 \x01(\t\x12\x0f\n\x07snippet\x18\x04 \x03(\t\x12\x15\n\rrecentChanges\x18\x05 \x01(\t\x12(\n\x0f\x61utoTranslation\x18\x06 \x03(\x0b\x32\x0f.TranslatedText\x12\x15\n\x05offer\x18\x07 \x03(\x0b\x32\x06.Offer\x12\x11\n\tchannelId\x18\t \x01(\x03\x12\x18\n\x05\x63hild\x18\n \x03(\x0b\x32\t.Document\x12\x1d\n\ndecoration\x18\x0b \x03(\x0b\x32\t.Document\"\xe6\x02\n\x05Image\x12\x11\n\timageType\x18\x01 \x01(\x05\x12#\n\tdimension\x18\x02 \x01(\n2\x10.Image.Dimension\x12\x10\n\x08imageUrl\x18\x05 \x01(\t\x12\x18\n\x10\x61ltTextLocalized\x18\x06 \x01(\t\x12\x11\n\tsecureUrl\x18\x07 \x01(\t\x12\x1a\n\x12positionInSequence\x18\x08 \x01(\x05\x12\x1e\n\x16supportsFifeUrlOptions\x18\t \x01(\x08\x12!\n\x08\x63itation\x18\n \x01(\n2\x0f.Image.Citation\x12\r\n\x05\x63olor\x18\x0f \x01(\t\x12\x1b\n\x13screenshotSetNumber\x18\x15 \x01(\x05\x1a*\n\tDimension\x12\r\n\x05width\x18\x03 \x01(\x05\x12\x0e\n\x06height\x18\x04 \x01(\x05\x1a/\n\x08\x43itation\x12\x16\n\x0etitleLocalized\x18\x0b \x01(\t\x12\x0b\n\x03url\x18\x0c \x01(\t\"J\n\x0eTranslatedText\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x14\n\x0csourceLocale\x18\x02 \x01(\t\x12\x14\n\x0ctargetLocale\x18\x03 \x01(\t\"i\n\x0bPlusOneData\x12\x11\n\tsetByUser\x18\x01 \x01(\x08\x12\r\n\x05total\x18\x02 \x01(\x03\x12\x14\n\x0c\x63irclesTotal\x18\x03 \x01(\x03\x12\"\n\rcirclesPeople\x18\x04 \x03(\x0b\x32\x0b.PlusPerson\":\n\nPlusPerson\x12\x13\n\x0b\x64isplayName\x18\x02 \x01(\t\x12\x17\n\x0fprofileImageUrl\x18\x04 \x01(\t\"c\n\x0c\x41lbumDetails\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x1e\n\x07\x64\x65tails\x18\x02 \x01(\x0b\x32\r.MusicDetails\x12%\n\rdisplayArtist\x18\x03 \x01(\x0b\x32\x0e.ArtistDetails\"\xfd\x04\n\nAppDetails\x12\x15\n\rdeveloperName\x18\x01 \x01(\t\x12\x1a\n\x12majorVersionNumber\x18\x02 \x01(\x05\x12\x13\n\x0bversionCode\x18\x03 \x01(\x05\x12\x15\n\rversionString\x18\x04 \x01(\t\x12\r\n\x05title\x18\x05 \x01(\t\x12\x13\n\x0b\x61ppCategory\x18\x07 \x03(\t\x12\x15\n\rcontentRating\x18\x08 \x01(\x05\x12\x18\n\x10installationSize\x18\t \x01(\x03\x12\x12\n\npermission\x18\n \x03(\t\x12\x16\n\x0e\x64\x65veloperEmail\x18\x0b \x01(\t\x12\x18\n\x10\x64\x65veloperWebsite\x18\x0c \x01(\t\x12\x14\n\x0cnumDownloads\x18\r \x01(\t\x12\x13\n\x0bpackageName\x18\x0e \x01(\t\x12\x19\n\x11recentChangesHtml\x18\x0f \x01(\t\x12\x12\n\nuploadDate\x18\x10 \x01(\t\x12\x1b\n\x04\x66ile\x18\x11 \x03(\x0b\x32\r.FileMetadata\x12\x0f\n\x07\x61ppType\x18\x12 \x01(\t\x12\x10\n\x08unstable\x18\x15 \x01(\x08\x12\x16\n\x0ehasInstantLink\x18\x18 \x01(\x08\x12\x13\n\x0b\x63ontainsAds\x18\x1e \x01(\t\x12#\n\x0c\x64\x65pendencies\x18\" \x01(\x0b\x32\r.Dependencies\x12/\n\x12testingProgramInfo\x18# \x01(\x0b\x32\x13.TestingProgramInfo\x12)\n\x0f\x65\x61rlyAccessInfo\x18$ \x01(\x0b\x32\x10.EarlyAccessInfo\x12\x13\n\x0binstantLink\x18+ \x01(\t\x12\x18\n\x10\x64\x65veloperAddress\x18- \x01(\t\"e\n\x0c\x44\x65pendencies\x12\x10\n\x08unknown1\x18\x01 \x01(\x05\x12\x10\n\x08unknown2\x18\x02 \x01(\x03\x12\x1f\n\ndependency\x18\x03 \x03(\x0b\x32\x0b.Dependency\x12\x10\n\x08unknown3\x18\x04 \x01(\x05\"D\n\nDependency\x12\x13\n\x0bpackageName\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x05\x12\x10\n\x08unknown4\x18\x04 \x01(\x05\"Z\n\x12TestingProgramInfo\x12\x12\n\nsubscribed\x18\x02 \x01(\x08\x12\x13\n\x0bsubscribed1\x18\x03 \x01(\x08\x12\x1b\n\x13testingProgramEmail\x18\x05 \x01(\t\" \n\x0f\x45\x61rlyAccessInfo\x12\r\n\x05\x65mail\x18\x03 \x01(\t\"^\n\rArtistDetails\x12\x12\n\ndetailsUrl\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12+\n\rexternalLinks\x18\x03 \x01(\x0b\x32\x14.ArtistExternalLinks\"b\n\x13\x41rtistExternalLinks\x12\x12\n\nwebsiteUrl\x18\x01 \x03(\t\x12\x1c\n\x14googlePlusProfileUrl\x18\x02 \x01(\t\x12\x19\n\x11youtubeChannelUrl\x18\x03 \x01(\t\"\xc6\x03\n\x0f\x44ocumentDetails\x12\x1f\n\nappDetails\x18\x01 \x01(\x0b\x32\x0b.AppDetails\x12#\n\x0c\x61lbumDetails\x18\x02 \x01(\x0b\x32\r.AlbumDetails\x12%\n\rartistDetails\x18\x03 \x01(\x0b\x32\x0e.ArtistDetails\x12!\n\x0bsongDetails\x18\x04 \x01(\x0b\x32\x0c.SongDetails\x12!\n\x0b\x62ookDetails\x18\x05 \x01(\x0b\x32\x0c.BookDetails\x12#\n\x0cvideoDetails\x18\x06 \x01(\x0b\x32\r.VideoDetails\x12\x31\n\x13subscriptionDetails\x18\x07 \x01(\x0b\x32\x14.SubscriptionDetails\x12)\n\x0fmagazineDetails\x18\x08 \x01(\x0b\x32\x10.MagazineDetails\x12%\n\rtvShowDetails\x18\t \x01(\x0b\x32\x0e.TvShowDetails\x12)\n\x0ftvSeasonDetails\x18\n \x01(\x0b\x32\x10.TvSeasonDetails\x12+\n\x10tvEpisodeDetails\x18\x0b \x01(\x0b\x32\x11.TvEpisodeDetails\"C\n\x0c\x46ileMetadata\x12\x10\n\x08\x66ileType\x18\x01 \x01(\x05\x12\x13\n\x0bversionCode\x18\x02 \x01(\x05\x12\x0c\n\x04size\x18\x03 \x01(\x03\"\x94\x01\n\x0fMagazineDetails\x12\x18\n\x10parentDetailsUrl\x18\x01 \x01(\t\x12)\n!deviceAvailabilityDescriptionHtml\x18\x02 \x01(\t\x12\x16\n\x0epsvDescription\x18\x03 \x01(\t\x12$\n\x1c\x64\x65liveryFrequencyDescription\x18\x04 \x01(\t\"\xbb\x01\n\x0cMusicDetails\x12\x11\n\tcensoring\x18\x01 \x01(\x05\x12\x13\n\x0b\x64urationSec\x18\x02 \x01(\x05\x12\x1b\n\x13originalReleaseDate\x18\x03 \x01(\t\x12\r\n\x05label\x18\x04 \x01(\t\x12\x1e\n\x06\x61rtist\x18\x05 \x03(\x0b\x32\x0e.ArtistDetails\x12\r\n\x05genre\x18\x06 \x03(\t\x12\x13\n\x0breleaseDate\x18\x07 \x01(\t\x12\x13\n\x0breleaseType\x18\x08 \x03(\x05\"\x9e\x01\n\x0bSongDetails\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x1e\n\x07\x64\x65tails\x18\x02 \x01(\x0b\x32\r.MusicDetails\x12\x11\n\talbumName\x18\x03 \x01(\t\x12\x13\n\x0btrackNumber\x18\x04 \x01(\x05\x12\x12\n\npreviewUrl\x18\x05 \x01(\t\x12%\n\rdisplayArtist\x18\x06 \x01(\x0b\x32\x0e.ArtistDetails\"1\n\x13SubscriptionDetails\x12\x1a\n\x12subscriptionPeriod\x18\x01 \x01(\x05\"e\n\x07Trailer\x12\x11\n\ttrailerId\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x14\n\x0cthumbnailUrl\x18\x03 \x01(\t\x12\x10\n\x08watchUrl\x18\x04 \x01(\t\x12\x10\n\x08\x64uration\x18\x05 \x01(\t\"W\n\x10TvEpisodeDetails\x12\x18\n\x10parentDetailsUrl\x18\x01 \x01(\t\x12\x14\n\x0c\x65pisodeIndex\x18\x02 \x01(\x05\x12\x13\n\x0breleaseDate\x18\x03 \x01(\t\"j\n\x0fTvSeasonDetails\x12\x18\n\x10parentDetailsUrl\x18\x01 \x01(\t\x12\x13\n\x0bseasonIndex\x18\x02 \x01(\x05\x12\x13\n\x0breleaseDate\x18\x03 \x01(\t\x12\x13\n\x0b\x62roadcaster\x18\x04 \x01(\t\"]\n\rTvShowDetails\x12\x13\n\x0bseasonCount\x18\x01 \x01(\x05\x12\x11\n\tstartYear\x18\x02 \x01(\x05\x12\x0f\n\x07\x65ndYear\x18\x03 \x01(\x05\x12\x13\n\x0b\x62roadcaster\x18\x04 \x01(\t\"?\n\x0bVideoCredit\x12\x12\n\ncreditType\x18\x01 \x01(\x05\x12\x0e\n\x06\x63redit\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x03(\t\"\xdb\x01\n\x0cVideoDetails\x12\x1c\n\x06\x63redit\x18\x01 \x03(\x0b\x32\x0c.VideoCredit\x12\x10\n\x08\x64uration\x18\x02 \x01(\t\x12\x13\n\x0breleaseDate\x18\x03 \x01(\t\x12\x15\n\rcontentRating\x18\x04 \x01(\t\x12\r\n\x05likes\x18\x05 \x01(\x03\x12\x10\n\x08\x64islikes\x18\x06 \x01(\x03\x12\r\n\x05genre\x18\x07 \x03(\t\x12\x19\n\x07trailer\x18\x08 \x03(\x0b\x32\x08.Trailer\x12$\n\nrentalTerm\x18\t \x03(\x0b\x32\x10.VideoRentalTerm\"\xa0\x01\n\x0fVideoRentalTerm\x12\x11\n\tofferType\x18\x01 \x01(\x05\x12\x19\n\x11offerAbbreviation\x18\x02 \x01(\t\x12\x14\n\x0crentalHeader\x18\x03 \x01(\t\x12#\n\x04term\x18\x04 \x03(\n2\x15.VideoRentalTerm.Term\x1a$\n\x04Term\x12\x0e\n\x06header\x18\x05 \x01(\t\x12\x0c\n\x04\x62ody\x18\x06 \x01(\t\"\xf9\x01\n\x06\x42ucket\x12\x18\n\x08\x64ocument\x18\x01 \x03(\x0b\x32\x06.DocV1\x12\x13\n\x0bmultiCorpus\x18\x02 \x01(\x08\x12\r\n\x05title\x18\x03 \x01(\t\x12\x0f\n\x07iconUrl\x18\x04 \x01(\t\x12\x17\n\x0f\x66ullContentsUrl\x18\x05 \x01(\t\x12\x11\n\trelevance\x18\x06 \x01(\x01\x12\x18\n\x10\x65stimatedResults\x18\x07 \x01(\x03\x12\x17\n\x0f\x61nalyticsCookie\x18\x08 \x01(\t\x12\x1b\n\x13\x66ullContentsListUrl\x18\t \x01(\t\x12\x13\n\x0bnextPageUrl\x18\n \x01(\t\x12\x0f\n\x07ordered\x18\x0b \x01(\x08\"<\n\x0cListResponse\x12\x17\n\x06\x62ucket\x18\x01 \x03(\x0b\x32\x07.Bucket\x12\x13\n\x03\x64oc\x18\x02 \x03(\x0b\x32\x06.DocV2\"\x94\x03\n\x05\x44ocV1\x12\x1c\n\tfinskyDoc\x18\x01 \x01(\x0b\x32\t.Document\x12\r\n\x05\x64ocid\x18\x02 \x01(\t\x12\x12\n\ndetailsUrl\x18\x03 \x01(\t\x12\x12\n\nreviewsUrl\x18\x04 \x01(\t\x12\x16\n\x0erelatedListUrl\x18\x05 \x01(\t\x12\x15\n\rmoreByListUrl\x18\x06 \x01(\t\x12\x10\n\x08shareUrl\x18\x07 \x01(\t\x12\x0f\n\x07\x63reator\x18\x08 \x01(\t\x12!\n\x07\x64\x65tails\x18\t \x01(\x0b\x32\x10.DocumentDetails\x12\x17\n\x0f\x64\x65scriptionHtml\x18\n \x01(\t\x12\x18\n\x10relatedBrowseUrl\x18\x0b \x01(\t\x12\x17\n\x0fmoreByBrowseUrl\x18\x0c \x01(\t\x12\x15\n\rrelatedHeader\x18\r \x01(\t\x12\x14\n\x0cmoreByHeader\x18\x0e \x01(\t\x12\r\n\x05title\x18\x0f \x01(\t\x12!\n\x0bplusOneData\x18\x10 \x01(\x0b\x32\x0c.PlusOneData\x12\x16\n\x0ewarningMessage\x18\x11 \x01(\t\"\xd7\x05\n\x05\x44ocV2\x12\r\n\x05\x64ocid\x18\x01 \x01(\t\x12\x14\n\x0c\x62\x61\x63kendDocid\x18\x02 \x01(\t\x12\x0f\n\x07\x64ocType\x18\x03 \x01(\x05\x12\x11\n\tbackendId\x18\x04 \x01(\x05\x12\r\n\x05title\x18\x05 \x01(\t\x12\x0f\n\x07\x63reator\x18\x06 \x01(\t\x12\x17\n\x0f\x64\x65scriptionHtml\x18\x07 \x01(\t\x12\x15\n\x05offer\x18\x08 \x03(\x0b\x32\x06.Offer\x12#\n\x0c\x61vailability\x18\t \x01(\x0b\x32\r.Availability\x12\x15\n\x05image\x18\n \x03(\x0b\x32\x06.Image\x12\x15\n\x05\x63hild\x18\x0b \x03(\x0b\x32\x06.DocV2\x12-\n\x11\x63ontainerMetadata\x18\x0c \x01(\x0b\x32\x12.ContainerMetadata\x12!\n\x07\x64\x65tails\x18\r \x01(\x0b\x32\x10.DocumentDetails\x12)\n\x0f\x61ggregateRating\x18\x0e \x01(\x0b\x32\x10.AggregateRating\x12#\n\x0crelatedLinks\x18\x0f \x01(\x0b\x32\r.RelatedLinks\x12\x12\n\ndetailsUrl\x18\x10 \x01(\t\x12\x10\n\x08shareUrl\x18\x11 \x01(\t\x12\x12\n\nreviewsUrl\x18\x12 \x01(\t\x12\x12\n\nbackendUrl\x18\x13 \x01(\t\x12\x1a\n\x12purchaseDetailsUrl\x18\x14 \x01(\t\x12\x17\n\x0f\x64\x65tailsReusable\x18\x15 \x01(\x08\x12\x10\n\x08subtitle\x18\x16 \x01(\t\x12;\n\x18unknownCategoryContainer\x18\x18 \x01(\x0b\x32\x19.UnknownCategoryContainer\x12\x1d\n\tunknown25\x18\x19 \x01(\x0b\x32\n.Unknown25\x12\x18\n\x10\x64\x65scriptionShort\x18\x1b \x01(\t\x12\x19\n\x11reviewSnippetsUrl\x18\x1f \x01(\t\x12\x1a\n\x12reviewQuestionsUrl\x18\" \x01(\t\")\n\tUnknown25\x12\x1c\n\x04item\x18\x02 \x03(\x0b\x32\x0e.Unknown25Item\"F\n\rUnknown25Item\x12\r\n\x05label\x18\x01 \x01(\t\x12&\n\tcontainer\x18\x03 \x01(\x0b\x32\x13.Unknown25Container\"#\n\x12Unknown25Container\x12\r\n\x05value\x18\x02 \x01(\t\"\xd9\x01\n\x0cRelatedLinks\x12\'\n\x08unknown1\x18\n \x01(\x0b\x32\x15.RelatedLinksUnknown1\x12\x18\n\x10privacyPolicyUrl\x18\x12 \x01(\t\x12&\n\x10youMightAlsoLike\x18\x18 \x01(\x0b\x32\x0c.RelatedLink\x12\x15\n\x05rated\x18\x1d \x01(\x0b\x32\x06.Rated\x12\"\n\x0crelatedLinks\x18\" \x03(\x0b\x32\x0c.RelatedLink\x12#\n\x0c\x63\x61tegoryInfo\x18\x35 \x01(\x0b\x32\r.CategoryInfo\"?\n\x14RelatedLinksUnknown1\x12\'\n\x08unknown2\x18\x02 \x01(\x0b\x32\x15.RelatedLinksUnknown2\"<\n\x14RelatedLinksUnknown2\x12\x0f\n\x07homeUrl\x18\x02 \x01(\t\x12\x13\n\x0bnextPageUrl\x18\x03 \x01(\t\"H\n\x05Rated\x12\r\n\x05label\x18\x01 \x01(\t\x12\x15\n\x05image\x18\x02 \x01(\x0b\x32\x06.Image\x12\x19\n\x11learnMoreHtmlLink\x18\x04 \x01(\t\"8\n\x0bRelatedLink\x12\r\n\x05label\x18\x01 \x01(\t\x12\x0c\n\x04url1\x18\x02 \x01(\t\x12\x0c\n\x04url2\x18\x03 \x01(\t\"4\n\x0c\x43\x61tegoryInfo\x12\x0f\n\x07\x61ppType\x18\x01 \x01(\t\x12\x13\n\x0b\x61ppCategory\x18\x02 \x01(\t\"\x99\x01\n\x17\x45ncryptedSubscriberInfo\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\x12\x14\n\x0c\x65ncryptedKey\x18\x02 \x01(\t\x12\x11\n\tsignature\x18\x03 \x01(\t\x12\x12\n\ninitVector\x18\x04 \x01(\t\x12\x18\n\x10googleKeyVersion\x18\x05 \x01(\x05\x12\x19\n\x11\x63\x61rrierKeyVersion\x18\x06 \x01(\x05\"\xbd\x03\n\x0c\x41vailability\x12\x13\n\x0brestriction\x18\x05 \x01(\x05\x12\x11\n\tofferType\x18\x06 \x01(\x05\x12\x13\n\x04rule\x18\x07 \x01(\x0b\x32\x05.Rule\x12X\n perdeviceavailabilityrestriction\x18\t \x03(\n2..Availability.PerDeviceAvailabilityRestriction\x12\x18\n\x10\x61vailableIfOwned\x18\r \x01(\x08\x12\x19\n\x07install\x18\x0e \x03(\x0b\x32\x08.Install\x12)\n\nfilterInfo\x18\x10 \x01(\x0b\x32\x15.FilterEvaluationInfo\x12%\n\rownershipInfo\x18\x11 \x01(\x0b\x32\x0e.OwnershipInfo\x1a\x8e\x01\n PerDeviceAvailabilityRestriction\x12\x11\n\tandroidId\x18\n \x01(\x06\x12\x19\n\x11\x64\x65viceRestriction\x18\x0b \x01(\x05\x12\x11\n\tchannelId\x18\x0c \x01(\x03\x12)\n\nfilterInfo\x18\x0f \x01(\x0b\x32\x15.FilterEvaluationInfo\"?\n\x14\x46ilterEvaluationInfo\x12\'\n\x0eruleEvaluation\x18\x01 \x03(\x0b\x32\x0f.RuleEvaluation\"\xd4\x01\n\x04Rule\x12\x0e\n\x06negate\x18\x01 \x01(\x08\x12\x10\n\x08operator\x18\x02 \x01(\x05\x12\x0b\n\x03key\x18\x03 \x01(\x05\x12\x11\n\tstringArg\x18\x04 \x03(\t\x12\x0f\n\x07longArg\x18\x05 \x03(\x03\x12\x11\n\tdoubleArg\x18\x06 \x03(\x01\x12\x16\n\x07subrule\x18\x07 \x03(\x0b\x32\x05.Rule\x12\x14\n\x0cresponseCode\x18\x08 \x01(\x05\x12\x0f\n\x07\x63omment\x18\t \x01(\t\x12\x15\n\rstringArgHash\x18\n \x03(\x06\x12\x10\n\x08\x63onstArg\x18\x0b \x03(\x05\"\x8d\x01\n\x0eRuleEvaluation\x12\x13\n\x04rule\x18\x01 \x01(\x0b\x32\x05.Rule\x12\x19\n\x11\x61\x63tualStringValue\x18\x02 \x03(\t\x12\x17\n\x0f\x61\x63tualLongValue\x18\x03 \x03(\x03\x12\x17\n\x0f\x61\x63tualBoolValue\x18\x04 \x03(\x08\x12\x19\n\x11\x61\x63tualDoubleValue\x18\x05 \x03(\x01\"v\n\x11LibraryAppDetails\x12\x17\n\x0f\x63\x65rtificateHash\x18\x02 \x01(\t\x12\"\n\x1arefundTimeoutTimestampMsec\x18\x03 \x01(\x03\x12$\n\x1cpostDeliveryRefundWindowMsec\x18\x04 \x01(\x03\"D\n\x13LibraryInAppDetails\x12\x1a\n\x12signedPurchaseData\x18\x01 \x01(\t\x12\x11\n\tsignature\x18\x02 \x01(\t\"\xf0\x01\n\x0fLibraryMutation\x12\x15\n\x05\x64ocid\x18\x01 \x01(\x0b\x32\x06.Docid\x12\x11\n\tofferType\x18\x02 \x01(\x05\x12\x14\n\x0c\x64ocumentHash\x18\x03 \x01(\x03\x12\x0f\n\x07\x64\x65leted\x18\x04 \x01(\x08\x12&\n\nappDetails\x18\x05 \x01(\x0b\x32\x12.LibraryAppDetails\x12\x38\n\x13subscriptionDetails\x18\x06 \x01(\x0b\x32\x1b.LibrarySubscriptionDetails\x12*\n\x0cinAppDetails\x18\x07 \x01(\x0b\x32\x14.LibraryInAppDetails\"\x95\x01\n\x1aLibrarySubscriptionDetails\x12\x1f\n\x17initiationTimestampMsec\x18\x01 \x01(\x03\x12\x1f\n\x17validUntilTimestampMsec\x18\x02 \x01(\x03\x12\x14\n\x0c\x61utoRenewing\x18\x03 \x01(\x08\x12\x1f\n\x17trialUntilTimestampMsec\x18\x04 \x01(\x03\"\x8c\x01\n\rLibraryUpdate\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0e\n\x06\x63orpus\x18\x02 \x01(\x05\x12\x13\n\x0bserverToken\x18\x03 \x01(\x0c\x12\"\n\x08mutation\x18\x04 \x03(\x0b\x32\x10.LibraryMutation\x12\x0f\n\x07hasMore\x18\x05 \x01(\x08\x12\x11\n\tlibraryId\x18\x06 \x01(\t\"B\n\x1a\x41ndroidAppNotificationData\x12\x13\n\x0bversionCode\x18\x01 \x01(\x05\x12\x0f\n\x07\x61ssetId\x18\x02 \x01(\t\"M\n\x15InAppNotificationData\x12\x17\n\x0f\x63heckoutOrderId\x18\x01 \x01(\t\x12\x1b\n\x13inAppNotificationId\x18\x02 \x01(\t\"#\n\x10LibraryDirtyData\x12\x0f\n\x07\x62\x61\x63kend\x18\x01 \x01(\x05\"\x97\x04\n\x0cNotification\x12\x18\n\x10notificationType\x18\x01 \x01(\x05\x12\x11\n\ttimestamp\x18\x03 \x01(\x03\x12\x15\n\x05\x64ocid\x18\x04 \x01(\x0b\x32\x06.Docid\x12\x10\n\x08\x64ocTitle\x18\x05 \x01(\t\x12\x11\n\tuserEmail\x18\x06 \x01(\t\x12,\n\x07\x61ppData\x18\x07 \x01(\x0b\x32\x1b.AndroidAppNotificationData\x12\x30\n\x0f\x61ppDeliveryData\x18\x08 \x01(\x0b\x32\x17.AndroidAppDeliveryData\x12\x31\n\x13purchaseRemovalData\x18\t \x01(\x0b\x32\x14.PurchaseRemovalData\x12\x33\n\x14userNotificationData\x18\n \x01(\x0b\x32\x15.UserNotificationData\x12\x35\n\x15inAppNotificationData\x18\x0b \x01(\x0b\x32\x16.InAppNotificationData\x12\x33\n\x14purchaseDeclinedData\x18\x0c \x01(\x0b\x32\x15.PurchaseDeclinedData\x12\x16\n\x0enotificationId\x18\r \x01(\t\x12%\n\rlibraryUpdate\x18\x0e \x01(\x0b\x32\x0e.LibraryUpdate\x12+\n\x10libraryDirtyData\x18\x0f \x01(\x0b\x32\x11.LibraryDirtyData\"@\n\x14PurchaseDeclinedData\x12\x0e\n\x06reason\x18\x01 \x01(\x05\x12\x18\n\x10showNotification\x18\x02 \x01(\x08\"(\n\x13PurchaseRemovalData\x12\x11\n\tmalicious\x18\x01 \x01(\x08\"\x88\x01\n\x14UserNotificationData\x12\x19\n\x11notificationTitle\x18\x01 \x01(\t\x12\x18\n\x10notificationText\x18\x02 \x01(\t\x12\x12\n\ntickerText\x18\x03 \x01(\t\x12\x13\n\x0b\x64ialogTitle\x18\x04 \x01(\t\x12\x12\n\ndialogText\x18\x05 \x01(\t\"\xa7\x02\n\x0f\x41ggregateRating\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x12\n\nstarRating\x18\x02 \x01(\x02\x12\x14\n\x0cratingsCount\x18\x03 \x01(\x04\x12\x16\n\x0eoneStarRatings\x18\x04 \x01(\x04\x12\x16\n\x0etwoStarRatings\x18\x05 \x01(\x04\x12\x18\n\x10threeStarRatings\x18\x06 \x01(\x04\x12\x17\n\x0f\x66ourStarRatings\x18\x07 \x01(\x04\x12\x17\n\x0f\x66iveStarRatings\x18\x08 \x01(\x04\x12\x15\n\rthumbsUpCount\x18\t \x01(\x04\x12\x17\n\x0fthumbsDownCount\x18\n \x01(\x04\x12\x14\n\x0c\x63ommentCount\x18\x0b \x01(\x04\x12\x1a\n\x12\x62\x61yesianMeanRating\x18\x0c \x01(\x01\"\x13\n\x11\x41\x63\x63\x65ptTosResponse\"\xe9\x01\n\x14\x43\x61rrierBillingConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\napiVersion\x18\x03 \x01(\x05\x12\x17\n\x0fprovisioningUrl\x18\x04 \x01(\t\x12\x16\n\x0e\x63redentialsUrl\x18\x05 \x01(\t\x12\x13\n\x0btosRequired\x18\x06 \x01(\x08\x12)\n!perTransactionCredentialsRequired\x18\x07 \x01(\x08\x12\x32\n*sendSubscriberIdWithCarrierBillingRequests\x18\x08 \x01(\x08\"^\n\rBillingConfig\x12\x33\n\x14\x63\x61rrierBillingConfig\x18\x01 \x01(\x0b\x32\x15.CarrierBillingConfig\x12\x18\n\x10maxIabApiVersion\x18\x02 \x01(\x05\"\x81\x01\n\x0e\x43orpusMetadata\x12\x0f\n\x07\x62\x61\x63kend\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nlandingUrl\x18\x03 \x01(\t\x12\x13\n\x0blibraryName\x18\x04 \x01(\t\x12\x15\n\rrecsWidgetUrl\x18\x06 \x01(\t\x12\x10\n\x08shopName\x18\x07 \x01(\t\"#\n\x0b\x45xperiments\x12\x14\n\x0c\x65xperimentId\x18\x01 \x03(\t\"3\n\x10SelfUpdateConfig\x12\x1f\n\x17latestClientVersionCode\x18\x01 \x01(\x05\"\xb1\x04\n\x0bTocResponse\x12\x1f\n\x06\x63orpus\x18\x01 \x03(\x0b\x32\x0f.CorpusMetadata\x12\x1c\n\x14tosVersionDeprecated\x18\x02 \x01(\x05\x12\x12\n\ntosContent\x18\x03 \x01(\t\x12\x0f\n\x07homeUrl\x18\x04 \x01(\t\x12!\n\x0b\x65xperiments\x18\x05 \x01(\x0b\x32\x0c.Experiments\x12&\n\x1etosCheckboxTextMarketingEmails\x18\x06 \x01(\t\x12\x10\n\x08tosToken\x18\x07 \x01(\t\x12\x17\n\x0ficonOverrideUrl\x18\t \x01(\t\x12+\n\x10selfUpdateConfig\x18\n \x01(\x0b\x32\x11.SelfUpdateConfig\x12\"\n\x1arequiresUploadDeviceConfig\x18\x0b \x01(\x08\x12%\n\rbillingConfig\x18\x0c \x01(\x0b\x32\x0e.BillingConfig\x12\x15\n\rrecsWidgetUrl\x18\r \x01(\t\x12\x15\n\rsocialHomeUrl\x18\x0f \x01(\t\x12\x1f\n\x17\x61geVerificationRequired\x18\x10 \x01(\x08\x12\x1a\n\x12gplusSignupEnabled\x18\x11 \x01(\x08\x12\x15\n\rredeemEnabled\x18\x12 \x01(\x08\x12\x0f\n\x07helpUrl\x18\x13 \x01(\t\x12\x0f\n\x07themeId\x18\x14 \x01(\x05\x12\x1c\n\x14\x65ntertainmentHomeUrl\x18\x15 \x01(\t\x12\x0e\n\x06\x63ookie\x18\x16 \x01(\t\"\xfe\x05\n\x07Payload\x12#\n\x0clistResponse\x18\x01 \x01(\x0b\x32\r.ListResponse\x12)\n\x0f\x64\x65tailsResponse\x18\x02 \x01(\x0b\x32\x10.DetailsResponse\x12\'\n\x0ereviewResponse\x18\x03 \x01(\x0b\x32\x0f.ReviewResponse\x12!\n\x0b\x62uyResponse\x18\x04 \x01(\x0b\x32\x0c.BuyResponse\x12\'\n\x0esearchResponse\x18\x05 \x01(\x0b\x32\x0f.SearchResponse\x12!\n\x0btocResponse\x18\x06 \x01(\x0b\x32\x0c.TocResponse\x12\'\n\x0e\x62rowseResponse\x18\x07 \x01(\x0b\x32\x0f.BrowseResponse\x12\x37\n\x16purchaseStatusResponse\x18\x08 \x01(\x0b\x32\x17.PurchaseStatusResponse\x12\x13\n\x0blogResponse\x18\n \x01(\t\x12\x1b\n\x13\x66lagContentResponse\x18\r \x01(\t\x12\x31\n\x13\x62ulkDetailsResponse\x18\x13 \x01(\x0b\x32\x14.BulkDetailsResponse\x12+\n\x10\x64\x65liveryResponse\x18\x15 \x01(\x0b\x32\x11.DeliveryResponse\x12-\n\x11\x61\x63\x63\x65ptTosResponse\x18\x16 \x01(\x0b\x32\x12.AcceptTosResponse\x12\x37\n\x16\x61ndroidCheckinResponse\x18\x1a \x01(\x0b\x32\x17.AndroidCheckinResponse\x12?\n\x1auploadDeviceConfigResponse\x18\x1c \x01(\x0b\x32\x1b.UploadDeviceConfigResponse\x12\x35\n\x15searchSuggestResponse\x18( \x01(\x0b\x32\x16.SearchSuggestResponse\x12\x37\n\x16testingProgramResponse\x18P \x01(\x0b\x32\x17.TestingProgramResponse\"g\n\x08PreFetch\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\"\n\x08response\x18\x02 \x01(\x0b\x32\x10.ResponseWrapper\x12\x0c\n\x04\x65tag\x18\x03 \x01(\t\x12\x0b\n\x03ttl\x18\x04 \x01(\x03\x12\x0f\n\x07softTtl\x18\x05 \x01(\x03\"\'\n\x0eServerMetadata\x12\x15\n\rlatencyMillis\x18\x01 \x01(\x03\".\n\x07Targets\x12\x10\n\x08targetId\x18\x01 \x03(\x03\x12\x11\n\tsignature\x18\x02 \x01(\x0c\"+\n\x0cServerCookie\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\r\n\x05token\x18\x02 \x01(\x0c\"4\n\rServerCookies\x12#\n\x0cserverCookie\x18\x01 \x03(\x0b\x32\r.ServerCookie\"\x96\x02\n\x0fResponseWrapper\x12\x19\n\x07payload\x18\x01 \x01(\x0b\x32\x08.Payload\x12!\n\x08\x63ommands\x18\x02 \x01(\x0b\x32\x0f.ServerCommands\x12\x1b\n\x08preFetch\x18\x03 \x03(\x0b\x32\t.PreFetch\x12#\n\x0cnotification\x18\x04 \x03(\x0b\x32\r.Notification\x12\'\n\x0eserverMetadata\x18\x05 \x01(\x0b\x32\x0f.ServerMetadata\x12\x19\n\x07targets\x18\x06 \x01(\x0b\x32\x08.Targets\x12%\n\rserverCookies\x18\x07 \x01(\x0b\x32\x0e.ServerCookies\x12\x18\n\x10serverLogsCookie\x18\t \x01(\x0c\"2\n\x12ResponseWrapperApi\x12\x1c\n\x07payload\x18\x01 \x01(\x0b\x32\x0b.PayloadApi\"?\n\nPayloadApi\x12\x31\n\x13userProfileResponse\x18\x05 \x01(\x0b\x32\x14.UserProfileResponse\"8\n\x13UserProfileResponse\x12!\n\x0buserProfile\x18\x01 \x01(\x0b\x32\x0c.UserProfile\"]\n\x0eServerCommands\x12\x12\n\nclearCache\x18\x01 \x01(\x08\x12\x1b\n\x13\x64isplayErrorMessage\x18\x02 \x01(\t\x12\x1a\n\x12logErrorStacktrace\x18\x03 \x01(\t\"D\n\x12GetReviewsResponse\x12\x17\n\x06review\x18\x01 \x03(\x0b\x32\x07.Review\x12\x15\n\rmatchingCount\x18\x02 \x01(\x03\"\xb5\x02\n\x06Review\x12\x12\n\nauthorName\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\x0e\n\x06source\x18\x03 \x01(\t\x12\x17\n\x0f\x64ocumentVersion\x18\x04 \x01(\t\x12\x15\n\rtimestampMsec\x18\x05 \x01(\x03\x12\x12\n\nstarRating\x18\x06 \x01(\x05\x12\r\n\x05title\x18\x07 \x01(\t\x12\x0f\n\x07\x63omment\x18\x08 \x01(\t\x12\x11\n\tcommentId\x18\t \x01(\t\x12\x12\n\ndeviceName\x18\x13 \x01(\t\x12\x11\n\treplyText\x18\x1d \x01(\t\x12\x1a\n\x12replyTimestampMsec\x18\x1e \x01(\x03\x12\x1d\n\x06\x61uthor\x18\x1f \x01(\x0b\x32\r.ReviewAuthor\x12!\n\x0buserProfile\x18! \x01(\x0b\x32\x0c.UserProfile\"4\n\x0cReviewAuthor\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x16\n\x06\x61vatar\x18\x05 \x01(\x0b\x32\x06.Image\"\xb2\x01\n\x0bUserProfile\x12\x16\n\x0epersonIdString\x18\x01 \x01(\t\x12\x10\n\x08personId\x18\x02 \x01(\t\x12\x10\n\x08unknown1\x18\x03 \x01(\x05\x12\x10\n\x08unknown2\x18\x04 \x01(\x05\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\x15\n\x05image\x18\n \x03(\x0b\x32\x06.Image\x12\x15\n\rgooglePlusUrl\x18\x13 \x01(\t\x12\x19\n\x11googlePlusTagline\x18\x16 \x01(\t\"l\n\x0eReviewResponse\x12(\n\x0bgetResponse\x18\x01 \x01(\x0b\x32\x13.GetReviewsResponse\x12\x13\n\x0bnextPageUrl\x18\x02 \x01(\t\x12\x1b\n\nuserReview\x18\x03 \x01(\x0b\x32\x07.Review\"g\n\rRelatedSearch\x12\x11\n\tsearchUrl\x18\x01 \x01(\t\x12\x0e\n\x06header\x18\x02 \x01(\t\x12\x11\n\tbackendId\x18\x03 \x01(\x05\x12\x0f\n\x07\x64ocType\x18\x04 \x01(\x05\x12\x0f\n\x07\x63urrent\x18\x05 \x01(\x08\"\xc1\x01\n\x0eSearchResponse\x12\x15\n\roriginalQuery\x18\x01 \x01(\t\x12\x16\n\x0esuggestedQuery\x18\x02 \x01(\t\x12\x16\n\x0e\x61ggregateQuery\x18\x03 \x01(\x08\x12\x17\n\x06\x62ucket\x18\x04 \x03(\x0b\x32\x07.Bucket\x12\x13\n\x03\x64oc\x18\x05 \x03(\x0b\x32\x06.DocV2\x12%\n\rrelatedSearch\x18\x06 \x03(\x0b\x32\x0e.RelatedSearch\x12\x13\n\x0bnextPageUrl\x18\n \x01(\t\";\n\x15SearchSuggestResponse\x12\"\n\x05\x65ntry\x18\x01 \x03(\x0b\x32\x13.SearchSuggestEntry\"\x9e\x02\n\x12SearchSuggestEntry\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x16\n\x0esuggestedQuery\x18\x02 \x01(\t\x12:\n\x0eimageContainer\x18\x05 \x01(\x0b\x32\".SearchSuggestEntry.ImageContainer\x12\r\n\x05title\x18\x06 \x01(\t\x12\x46\n\x14packageNameContainer\x18\x08 \x01(\x0b\x32(.SearchSuggestEntry.PackageNameContainer\x1a\"\n\x0eImageContainer\x12\x10\n\x08imageUrl\x18\x05 \x01(\t\x1a+\n\x14PackageNameContainer\x12\x13\n\x0bpackageName\x18\x01 \x01(\t\"?\n\x16TestingProgramResponse\x12%\n\x06result\x18\x02 \x01(\x0b\x32\x15.TestingProgramResult\"?\n\x14TestingProgramResult\x12\'\n\x07\x64\x65tails\x18\x04 \x01(\x0b\x32\x16.TestingProgramDetails\"H\n\x15TestingProgramDetails\x12\r\n\x05\x66lag1\x18\x02 \x01(\x08\x12\n\n\x02id\x18\x03 \x01(\x03\x12\x14\n\x0cunsubscribed\x18\x04 \x01(\x08\"B\n\nLogRequest\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\x12!\n\x19\x64ownloadConfirmationQuery\x18\x02 \x01(\t\"?\n\x15TestingProgramRequest\x12\x13\n\x0bpackageName\x18\x01 \x01(\t\x12\x11\n\tsubscribe\x18\x02 \x01(\x08\"\x84\x01\n\x19UploadDeviceConfigRequest\x12\x36\n\x13\x64\x65viceConfiguration\x18\x01 \x01(\x0b\x32\x19.DeviceConfigurationProto\x12\x14\n\x0cmanufacturer\x18\x02 \x01(\t\x12\x19\n\x11gcmRegistrationId\x18\x03 \x01(\t\"=\n\x1aUploadDeviceConfigResponse\x12\x1f\n\x17uploadDeviceConfigToken\x18\x01 \x01(\t\"\xe7\x03\n\x15\x41ndroidCheckinRequest\x12\x0c\n\x04imei\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x03\x12\x0e\n\x06\x64igest\x18\x03 \x01(\t\x12%\n\x07\x63heckin\x18\x04 \x01(\x0b\x32\x14.AndroidCheckinProto\x12\x14\n\x0c\x64\x65siredBuild\x18\x05 \x01(\t\x12\x0e\n\x06locale\x18\x06 \x01(\t\x12\x11\n\tloggingId\x18\x07 \x01(\x03\x12\x15\n\rmarketCheckin\x18\x08 \x01(\t\x12\x0f\n\x07macAddr\x18\t \x03(\t\x12\x0c\n\x04meid\x18\n \x01(\t\x12\x15\n\raccountCookie\x18\x0b \x03(\t\x12\x10\n\x08timeZone\x18\x0c \x01(\t\x12\x15\n\rsecurityToken\x18\r \x01(\x06\x12\x0f\n\x07version\x18\x0e \x01(\x05\x12\x0f\n\x07otaCert\x18\x0f \x03(\t\x12\x14\n\x0cserialNumber\x18\x10 \x01(\t\x12\x0b\n\x03\x65sn\x18\x11 \x01(\t\x12\x36\n\x13\x64\x65viceConfiguration\x18\x12 \x01(\x0b\x32\x19.DeviceConfigurationProto\x12\x13\n\x0bmacAddrType\x18\x13 \x03(\t\x12\x10\n\x08\x66ragment\x18\x14 \x01(\x05\x12\x10\n\x08userName\x18\x15 \x01(\t\x12\x18\n\x10userSerialNumber\x18\x16 \x01(\x05\"\xa4\x02\n\x16\x41ndroidCheckinResponse\x12\x0f\n\x07statsOk\x18\x01 \x01(\x08\x12#\n\x06intent\x18\x02 \x03(\x0b\x32\x13.AndroidIntentProto\x12\x10\n\x08timeMsec\x18\x03 \x01(\x03\x12\x0e\n\x06\x64igest\x18\x04 \x01(\t\x12\"\n\x07setting\x18\x05 \x03(\x0b\x32\x11.GservicesSetting\x12\x10\n\x08marketOk\x18\x06 \x01(\x08\x12\x11\n\tandroidId\x18\x07 \x01(\x06\x12\x15\n\rsecurityToken\x18\x08 \x01(\x06\x12\x14\n\x0csettingsDiff\x18\t \x01(\x08\x12\x15\n\rdeleteSetting\x18\n \x03(\t\x12%\n\x1d\x64\x65viceCheckinConsistencyToken\x18\x0c \x01(\t\"/\n\x10GservicesSetting\x12\x0c\n\x04name\x18\x01 \x01(\x0c\x12\r\n\x05value\x18\x02 \x01(\x0c\"\x94\x02\n\x11\x41ndroidBuildProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07product\x18\x02 \x01(\t\x12\x0f\n\x07\x63\x61rrier\x18\x03 \x01(\t\x12\r\n\x05radio\x18\x04 \x01(\t\x12\x12\n\nbootloader\x18\x05 \x01(\t\x12\x0e\n\x06\x63lient\x18\x06 \x01(\t\x12\x11\n\ttimestamp\x18\x07 \x01(\x03\x12\x16\n\x0egoogleServices\x18\x08 \x01(\x05\x12\x0e\n\x06\x64\x65vice\x18\t \x01(\t\x12\x12\n\nsdkVersion\x18\n \x01(\x05\x12\r\n\x05model\x18\x0b \x01(\t\x12\x14\n\x0cmanufacturer\x18\x0c \x01(\t\x12\x14\n\x0c\x62uildProduct\x18\r \x01(\t\x12\x14\n\x0cotaInstalled\x18\x0e \x01(\x08\"\x82\x02\n\x13\x41ndroidCheckinProto\x12!\n\x05\x62uild\x18\x01 \x01(\x0b\x32\x12.AndroidBuildProto\x12\x17\n\x0flastCheckinMsec\x18\x02 \x01(\x03\x12!\n\x05\x65vent\x18\x03 \x03(\x0b\x32\x12.AndroidEventProto\x12$\n\x04stat\x18\x04 \x03(\x0b\x32\x16.AndroidStatisticProto\x12\x16\n\x0erequestedGroup\x18\x05 \x03(\t\x12\x14\n\x0c\x63\x65llOperator\x18\x06 \x01(\t\x12\x13\n\x0bsimOperator\x18\x07 \x01(\t\x12\x0f\n\x07roaming\x18\x08 \x01(\t\x12\x12\n\nuserNumber\x18\t \x01(\x05\"A\n\x11\x41ndroidEventProto\x12\x0b\n\x03tag\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x10\n\x08timeMsec\x18\x03 \x01(\x03\"\xaa\x01\n\x12\x41ndroidIntentProto\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t\x12\x0f\n\x07\x64\x61taUri\x18\x02 \x01(\t\x12\x10\n\x08mimeType\x18\x03 \x01(\t\x12\x11\n\tjavaClass\x18\x04 \x01(\t\x12(\n\x05\x65xtra\x18\x05 \x03(\n2\x19.AndroidIntentProto.Extra\x1a$\n\x05\x45xtra\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\r\n\x05value\x18\x07 \x01(\t\"@\n\x15\x41ndroidStatisticProto\x12\x0b\n\x03tag\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x12\x0b\n\x03sum\x18\x03 \x01(\x02\"v\n\x12\x43lientLibraryState\x12\x0e\n\x06\x63orpus\x18\x01 \x01(\x05\x12\x13\n\x0bserverToken\x18\x02 \x01(\x0c\x12\x13\n\x0bhashCodeSum\x18\x03 \x01(\x03\x12\x13\n\x0blibrarySize\x18\x04 \x01(\x05\x12\x11\n\tlibraryId\x18\x05 \x01(\t\"\xe2\x01\n\x15\x41ndroidDataUsageProto\x12\x0f\n\x07version\x18\x01 \x01(\x05\x12\x19\n\x11\x63urrentReportMsec\x18\x02 \x01(\x03\x12\x39\n\x17keyToPackageNameMapping\x18\x03 \x03(\x0b\x32\x18.KeyToPackageNameMapping\x12\x31\n\x13payloadLevelAppStat\x18\x04 \x03(\x0b\x32\x14.PayloadLevelAppStat\x12/\n\x12ipLayerNetworkStat\x18\x05 \x03(\x0b\x32\x13.IpLayerNetworkStat\"n\n\x17\x41ndroidUsageStatsReport\x12\x11\n\tandroidId\x18\x01 \x01(\x03\x12\x11\n\tloggingId\x18\x02 \x01(\x03\x12-\n\nusageStats\x18\x03 \x01(\x0b\x32\x19.UsageStatsExtensionProto\"}\n\tAppBucket\x12\x17\n\x0f\x62ucketStartMsec\x18\x01 \x01(\x03\x12\x1a\n\x12\x62ucketDurationMsec\x18\x02 \x01(\x03\x12#\n\x0cstatCounters\x18\x03 \x03(\x0b\x32\r.StatCounters\x12\x16\n\x0eoperationCount\x18\x04 \x01(\x03\"-\n\x0b\x43ounterData\x12\r\n\x05\x62ytes\x18\x01 \x01(\x03\x12\x0f\n\x07packets\x18\x02 \x01(\x03\"b\n\x0eIpLayerAppStat\x12\x12\n\npackageKey\x18\x01 \x01(\x05\x12\x16\n\x0e\x61pplicationTag\x18\x02 \x01(\x05\x12$\n\x10ipLayerAppBucket\x18\x03 \x03(\x0b\x32\n.AppBucket\"\x8f\x01\n\x14IpLayerNetworkBucket\x12\x17\n\x0f\x62ucketStartMsec\x18\x01 \x01(\x03\x12\x1a\n\x12\x62ucketDurationMsec\x18\x02 \x01(\x03\x12#\n\x0cstatCounters\x18\x03 \x03(\x0b\x32\r.StatCounters\x12\x1d\n\x15networkActiveDuration\x18\x04 \x01(\x03\"\x98\x01\n\x12IpLayerNetworkStat\x12\x16\n\x0enetworkDetails\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\x05\x12\x33\n\x14ipLayerNetworkBucket\x18\x03 \x03(\x0b\x32\x15.IpLayerNetworkBucket\x12\'\n\x0eipLayerAppStat\x18\x04 \x03(\x0b\x32\x0f.IpLayerAppStat\"g\n\x17KeyToPackageNameMapping\x12\x12\n\npackageKey\x18\x01 \x01(\x05\x12\x0f\n\x07uidName\x18\x02 \x01(\t\x12\'\n\x11sharedPackageList\x18\x03 \x03(\x0b\x32\x0c.PackageInfo\"3\n\x0bPackageInfo\x12\x0f\n\x07pkgName\x18\x01 \x01(\t\x12\x13\n\x0bversionCode\x18\x02 \x01(\x05\"l\n\x13PayloadLevelAppStat\x12\x12\n\npackageKey\x18\x01 \x01(\x05\x12\x16\n\x0e\x61pplicationTag\x18\x02 \x01(\x05\x12)\n\x15payloadLevelAppBucket\x18\x03 \x03(\x0b\x32\n.AppBucket\"h\n\x0cStatCounters\x12\x14\n\x0cnetworkProto\x18\x01 \x01(\x05\x12\x11\n\tdirection\x18\x02 \x01(\x05\x12!\n\x0b\x63ounterData\x18\x03 \x01(\x0b\x32\x0c.CounterData\x12\x0c\n\x04\x66gBg\x18\x04 \x01(\x05\"E\n\x18UsageStatsExtensionProto\x12)\n\tdataUsage\x18\x01 \x01(\x0b\x32\x16.AndroidDataUsageProto\"\\\n\x14ModifyLibraryRequest\x12\x11\n\tlibraryId\x18\x01 \x01(\t\x12\x16\n\x0e\x61\x64\x64PackageName\x18\x02 \x03(\t\x12\x19\n\x11removePackageName\x18\x03 \x03(\t\"H\n\x11UrlRequestWrapper\x12\x33\n\x14\x64\x65veloperAppsRequest\x18\x31 \x01(\x0b\x32\x15.DeveloperAppsRequest\"\x97\x01\n\x14\x44\x65veloperAppsRequest\x12\x34\n\x15\x64\x65veloperIdContainer1\x18\x01 \x01(\x0b\x32\x15.DeveloperIdContainer\x12\x34\n\x15\x64\x65veloperIdContainer2\x18\x02 \x01(\x0b\x32\x15.DeveloperIdContainer\x12\x13\n\x0bunknownInt3\x18\x03 \x01(\x05\"U\n\x14\x44\x65veloperIdContainer\x12\x13\n\x0b\x64\x65veloperId\x18\x01 \x01(\t\x12\x13\n\x0bunknownInt2\x18\x02 \x01(\x05\x12\x13\n\x0bunknownInt3\x18\x03 \x01(\x05')

_ANDROIDAPPDELIVERYDATA = DESCRIPTOR.message_types_by_name['AndroidAppDeliveryData']
_SPLIT = DESCRIPTOR.message_types_by_name['Split']
_ANDROIDAPPPATCHDATA = DESCRIPTOR.message_types_by_name['AndroidAppPatchData']
_APPFILEMETADATA = DESCRIPTOR.message_types_by_name['AppFileMetadata']
_ENCRYPTIONPARAMS = DESCRIPTOR.message_types_by_name['EncryptionParams']
_HTTPCOOKIE = DESCRIPTOR.message_types_by_name['HttpCookie']
_ADDRESS = DESCRIPTOR.message_types_by_name['Address']
_BOOKAUTHOR = DESCRIPTOR.message_types_by_name['BookAuthor']
_BOOKDETAILS = DESCRIPTOR.message_types_by_name['BookDetails']
_BOOKDETAILS_IDENTIFIER = _BOOKDETAILS.nested_types_by_name['Identifier']
_BOOKSUBJECT = DESCRIPTOR.message_types_by_name['BookSubject']
_BROWSELINK = DESCRIPTOR.message_types_by_name['BrowseLink']
_UNKNOWNCATEGORYCONTAINER = DESCRIPTOR.message_types_by_name['UnknownCategoryContainer']
_CATEGORYIDCONTAINER = DESCRIPTOR.message_types_by_name['CategoryIdContainer']
_BROWSERESPONSE = DESCRIPTOR.message_types_by_name['BrowseResponse']
_CATEGORYCONTAINER = DESCRIPTOR.message_types_by_name['CategoryContainer']
_ADDRESSCHALLENGE = DESCRIPTOR.message_types_by_name['AddressChallenge']
_AUTHENTICATIONCHALLENGE = DESCRIPTOR.message_types_by_name['AuthenticationChallenge']
_BUYRESPONSE = DESCRIPTOR.message_types_by_name['BuyResponse']
_BUYRESPONSE_CHECKOUTINFO = _BUYRESPONSE.nested_types_by_name['CheckoutInfo']
_BUYRESPONSE_CHECKOUTINFO_CHECKOUTOPTION = _BUYRESPONSE_CHECKOUTINFO.nested_types_by_name['CheckoutOption']
_CHALLENGE = DESCRIPTOR.message_types_by_name['Challenge']
_FORMCHECKBOX = DESCRIPTOR.message_types_by_name['FormCheckbox']
_LINEITEM = DESCRIPTOR.message_types_by_name['LineItem']
_MONEY = DESCRIPTOR.message_types_by_name['Money']
_PURCHASENOTIFICATIONRESPONSE = DESCRIPTOR.message_types_by_name['PurchaseNotificationResponse']
_PURCHASESTATUSRESPONSE = DESCRIPTOR.message_types_by_name['PurchaseStatusResponse']
_DELIVERYRESPONSE = DESCRIPTOR.message_types_by_name['DeliveryResponse']
_DOCID = DESCRIPTOR.message_types_by_name['Docid']
_INSTALL = DESCRIPTOR.message_types_by_name['Install']
_OFFER = DESCRIPTOR.message_types_by_name['Offer']
_OWNERSHIPINFO = DESCRIPTOR.message_types_by_name['OwnershipInfo']
_RENTALTERMS = DESCRIPTOR.message_types_by_name['RentalTerms']
_SUBSCRIPTIONTERMS = DESCRIPTOR.message_types_by_name['SubscriptionTerms']
_TIMEPERIOD = DESCRIPTOR.message_types_by_name['TimePeriod']
_BILLINGADDRESSSPEC = DESCRIPTOR.message_types_by_name['BillingAddressSpec']
_CARRIERBILLINGCREDENTIALS = DESCRIPTOR.message_types_by_name['CarrierBillingCredentials']
_CARRIERBILLINGINSTRUMENT = DESCRIPTOR.message_types_by_name['CarrierBillingInstrument']
_CARRIERBILLINGINSTRUMENTSTATUS = DESCRIPTOR.message_types_by_name['CarrierBillingInstrumentStatus']
_CARRIERTOS = DESCRIPTOR.message_types_by_name['CarrierTos']
_CARRIERTOSENTRY = DESCRIPTOR.message_types_by_name['CarrierTosEntry']
_CREDITCARDINSTRUMENT = DESCRIPTOR.message_types_by_name['CreditCardInstrument']
_EFEPARAM = DESCRIPTOR.message_types_by_name['EfeParam']
_INPUTVALIDATIONERROR = DESCRIPTOR.message_types_by_name['InputValidationError']
_INSTRUMENT = DESCRIPTOR.message_types_by_name['Instrument']
_PASSWORDPROMPT = DESCRIPTOR.message_types_by_name['PasswordPrompt']
_CONTAINERMETADATA = DESCRIPTOR.message_types_by_name['ContainerMetadata']
_DEBUGINFO = DESCRIPTOR.message_types_by_name['DebugInfo']
_DEBUGINFO_TIMING = _DEBUGINFO.nested_types_by_name['Timing']
_BULKDETAILSENTRY = DESCRIPTOR.message_types_by_name['BulkDetailsEntry']
_BULKDETAILSREQUEST = DESCRIPTOR.message_types_by_name['BulkDetailsRequest']
_BULKDETAILSRESPONSE = DESCRIPTOR.message_types_by_name['BulkDetailsResponse']
_DETAILSRESPONSE = DESCRIPTOR.message_types_by_name['DetailsResponse']
_BADGE = DESCRIPTOR.message_types_by_name['Badge']
_BADGECONTAINER1 = DESCRIPTOR.message_types_by_name['BadgeContainer1']
_BADGECONTAINER2 = DESCRIPTOR.message_types_by_name['BadgeContainer2']
_BADGELINKCONTAINER = DESCRIPTOR.message_types_by_name['BadgeLinkContainer']
_FEATURES = DESCRIPTOR.message_types_by_name['Features']
_FEATURE = DESCRIPTOR.message_types_by_name['Feature']
_DEVICECONFIGURATIONPROTO = DESCRIPTOR.message_types_by_name['DeviceConfigurationProto']
_DOCUMENT = DESCRIPTOR.message_types_by_name['Document']
_DOCUMENTVARIANT = DESCRIPTOR.message_types_by_name['DocumentVariant']
_IMAGE = DESCRIPTOR.message_types_by_name['Image']
_IMAGE_DIMENSION = _IMAGE.nested_types_by_name['Dimension']
_IMAGE_CITATION = _IMAGE.nested_types_by_name['Citation']
_TRANSLATEDTEXT = DESCRIPTOR.message_types_by_name['TranslatedText']
_PLUSONEDATA = DESCRIPTOR.message_types_by_name['PlusOneData']
_PLUSPERSON = DESCRIPTOR.message_types_by_name['PlusPerson']
_ALBUMDETAILS = DESCRIPTOR.message_types_by_name['AlbumDetails']
_APPDETAILS = DESCRIPTOR.message_types_by_name['AppDetails']
_DEPENDENCIES = DESCRIPTOR.message_types_by_name['Dependencies']
_DEPENDENCY = DESCRIPTOR.message_types_by_name['Dependency']
_TESTINGPROGRAMINFO = DESCRIPTOR.message_types_by_name['TestingProgramInfo']
_EARLYACCESSINFO = DESCRIPTOR.message_types_by_name['EarlyAccessInfo']
_ARTISTDETAILS = DESCRIPTOR.message_types_by_name['ArtistDetails']
_ARTISTEXTERNALLINKS = DESCRIPTOR.message_types_by_name['ArtistExternalLinks']
_DOCUMENTDETAILS = DESCRIPTOR.message_types_by_name['DocumentDetails']
_FILEMETADATA = DESCRIPTOR.message_types_by_name['FileMetadata']
_MAGAZINEDETAILS = DESCRIPTOR.message_types_by_name['MagazineDetails']
_MUSICDETAILS = DESCRIPTOR.message_types_by_name['MusicDetails']
_SONGDETAILS = DESCRIPTOR.message_types_by_name['SongDetails']
_SUBSCRIPTIONDETAILS = DESCRIPTOR.message_types_by_name['SubscriptionDetails']
_TRAILER = DESCRIPTOR.message_types_by_name['Trailer']
_TVEPISODEDETAILS = DESCRIPTOR.message_types_by_name['TvEpisodeDetails']
_TVSEASONDETAILS = DESCRIPTOR.message_types_by_name['TvSeasonDetails']
_TVSHOWDETAILS = DESCRIPTOR.message_types_by_name['TvShowDetails']
_VIDEOCREDIT = DESCRIPTOR.message_types_by_name['VideoCredit']
_VIDEODETAILS = DESCRIPTOR.message_types_by_name['VideoDetails']
_VIDEORENTALTERM = DESCRIPTOR.message_types_by_name['VideoRentalTerm']
_VIDEORENTALTERM_TERM = _VIDEORENTALTERM.nested_types_by_name['Term']
_BUCKET = DESCRIPTOR.message_types_by_name['Bucket']
_LISTRESPONSE = DESCRIPTOR.message_types_by_name['ListResponse']
_DOCV1 = DESCRIPTOR.message_types_by_name['DocV1']
_DOCV2 = DESCRIPTOR.message_types_by_name['DocV2']
_UNKNOWN25 = DESCRIPTOR.message_types_by_name['Unknown25']
_UNKNOWN25ITEM = DESCRIPTOR.message_types_by_name['Unknown25Item']
_UNKNOWN25CONTAINER = DESCRIPTOR.message_types_by_name['Unknown25Container']
_RELATEDLINKS = DESCRIPTOR.message_types_by_name['RelatedLinks']
_RELATEDLINKSUNKNOWN1 = DESCRIPTOR.message_types_by_name['RelatedLinksUnknown1']
_RELATEDLINKSUNKNOWN2 = DESCRIPTOR.message_types_by_name['RelatedLinksUnknown2']
_RATED = DESCRIPTOR.message_types_by_name['Rated']
_RELATEDLINK = DESCRIPTOR.message_types_by_name['RelatedLink']
_CATEGORYINFO = DESCRIPTOR.message_types_by_name['CategoryInfo']
_ENCRYPTEDSUBSCRIBERINFO = DESCRIPTOR.message_types_by_name['EncryptedSubscriberInfo']
_AVAILABILITY = DESCRIPTOR.message_types_by_name['Availability']
_AVAILABILITY_PERDEVICEAVAILABILITYRESTRICTION = _AVAILABILITY.nested_types_by_name['PerDeviceAvailabilityRestriction']
_FILTEREVALUATIONINFO = DESCRIPTOR.message_types_by_name['FilterEvaluationInfo']
_RULE = DESCRIPTOR.message_types_by_name['Rule']
_RULEEVALUATION = DESCRIPTOR.message_types_by_name['RuleEvaluation']
_LIBRARYAPPDETAILS = DESCRIPTOR.message_types_by_name['LibraryAppDetails']
_LIBRARYINAPPDETAILS = DESCRIPTOR.message_types_by_name['LibraryInAppDetails']
_LIBRARYMUTATION = DESCRIPTOR.message_types_by_name['LibraryMutation']
_LIBRARYSUBSCRIPTIONDETAILS = DESCRIPTOR.message_types_by_name['LibrarySubscriptionDetails']
_LIBRARYUPDATE = DESCRIPTOR.message_types_by_name['LibraryUpdate']
_ANDROIDAPPNOTIFICATIONDATA = DESCRIPTOR.message_types_by_name['AndroidAppNotificationData']
_INAPPNOTIFICATIONDATA = DESCRIPTOR.message_types_by_name['InAppNotificationData']
_LIBRARYDIRTYDATA = DESCRIPTOR.message_types_by_name['LibraryDirtyData']
_NOTIFICATION = DESCRIPTOR.message_types_by_name['Notification']
_PURCHASEDECLINEDDATA = DESCRIPTOR.message_types_by_name['PurchaseDeclinedData']
_PURCHASEREMOVALDATA = DESCRIPTOR.message_types_by_name['PurchaseRemovalData']
_USERNOTIFICATIONDATA = DESCRIPTOR.message_types_by_name['UserNotificationData']
_AGGREGATERATING = DESCRIPTOR.message_types_by_name['AggregateRating']
_ACCEPTTOSRESPONSE = DESCRIPTOR.message_types_by_name['AcceptTosResponse']
_CARRIERBILLINGCONFIG = DESCRIPTOR.message_types_by_name['CarrierBillingConfig']
_BILLINGCONFIG = DESCRIPTOR.message_types_by_name['BillingConfig']
_CORPUSMETADATA = DESCRIPTOR.message_types_by_name['CorpusMetadata']
_EXPERIMENTS = DESCRIPTOR.message_types_by_name['Experiments']
_SELFUPDATECONFIG = DESCRIPTOR.message_types_by_name['SelfUpdateConfig']
_TOCRESPONSE = DESCRIPTOR.message_types_by_name['TocResponse']
_PAYLOAD = DESCRIPTOR.message_types_by_name['Payload']
_PREFETCH = DESCRIPTOR.message_types_by_name['PreFetch']
_SERVERMETADATA = DESCRIPTOR.message_types_by_name['ServerMetadata']
_TARGETS = DESCRIPTOR.message_types_by_name['Targets']
_SERVERCOOKIE = DESCRIPTOR.message_types_by_name['ServerCookie']
_SERVERCOOKIES = DESCRIPTOR.message_types_by_name['ServerCookies']
_RESPONSEWRAPPER = DESCRIPTOR.message_types_by_name['ResponseWrapper']
_RESPONSEWRAPPERAPI = DESCRIPTOR.message_types_by_name['ResponseWrapperApi']
_PAYLOADAPI = DESCRIPTOR.message_types_by_name['PayloadApi']
_USERPROFILERESPONSE = DESCRIPTOR.message_types_by_name['UserProfileResponse']
_SERVERCOMMANDS = DESCRIPTOR.message_types_by_name['ServerCommands']
_GETREVIEWSRESPONSE = DESCRIPTOR.message_types_by_name['GetReviewsResponse']
_REVIEW = DESCRIPTOR.message_types_by_name['Review']
_REVIEWAUTHOR = DESCRIPTOR.message_types_by_name['ReviewAuthor']
_USERPROFILE = DESCRIPTOR.message_types_by_name['UserProfile']
_REVIEWRESPONSE = DESCRIPTOR.message_types_by_name['ReviewResponse']
_RELATEDSEARCH = DESCRIPTOR.message_types_by_name['RelatedSearch']
_SEARCHRESPONSE = DESCRIPTOR.message_types_by_name['SearchResponse']
_SEARCHSUGGESTRESPONSE = DESCRIPTOR.message_types_by_name['SearchSuggestResponse']
_SEARCHSUGGESTENTRY = DESCRIPTOR.message_types_by_name['SearchSuggestEntry']
_SEARCHSUGGESTENTRY_IMAGECONTAINER = _SEARCHSUGGESTENTRY.nested_types_by_name['ImageContainer']
_SEARCHSUGGESTENTRY_PACKAGENAMECONTAINER = _SEARCHSUGGESTENTRY.nested_types_by_name['PackageNameContainer']
_TESTINGPROGRAMRESPONSE = DESCRIPTOR.message_types_by_name['TestingProgramResponse']
_TESTINGPROGRAMRESULT = DESCRIPTOR.message_types_by_name['TestingProgramResult']
_TESTINGPROGRAMDETAILS = DESCRIPTOR.message_types_by_name['TestingProgramDetails']
_LOGREQUEST = DESCRIPTOR.message_types_by_name['LogRequest']
_TESTINGPROGRAMREQUEST = DESCRIPTOR.message_types_by_name['TestingProgramRequest']
_UPLOADDEVICECONFIGREQUEST = DESCRIPTOR.message_types_by_name['UploadDeviceConfigRequest']
_UPLOADDEVICECONFIGRESPONSE = DESCRIPTOR.message_types_by_name['UploadDeviceConfigResponse']
_ANDROIDCHECKINREQUEST = DESCRIPTOR.message_types_by_name['AndroidCheckinRequest']
_ANDROIDCHECKINRESPONSE = DESCRIPTOR.message_types_by_name['AndroidCheckinResponse']
_GSERVICESSETTING = DESCRIPTOR.message_types_by_name['GservicesSetting']
_ANDROIDBUILDPROTO = DESCRIPTOR.message_types_by_name['AndroidBuildProto']
_ANDROIDCHECKINPROTO = DESCRIPTOR.message_types_by_name['AndroidCheckinProto']
_ANDROIDEVENTPROTO = DESCRIPTOR.message_types_by_name['AndroidEventProto']
_ANDROIDINTENTPROTO = DESCRIPTOR.message_types_by_name['AndroidIntentProto']
_ANDROIDINTENTPROTO_EXTRA = _ANDROIDINTENTPROTO.nested_types_by_name['Extra']
_ANDROIDSTATISTICPROTO = DESCRIPTOR.message_types_by_name['AndroidStatisticProto']
_CLIENTLIBRARYSTATE = DESCRIPTOR.message_types_by_name['ClientLibraryState']
_ANDROIDDATAUSAGEPROTO = DESCRIPTOR.message_types_by_name['AndroidDataUsageProto']
_ANDROIDUSAGESTATSREPORT = DESCRIPTOR.message_types_by_name['AndroidUsageStatsReport']
_APPBUCKET = DESCRIPTOR.message_types_by_name['AppBucket']
_COUNTERDATA = DESCRIPTOR.message_types_by_name['CounterData']
_IPLAYERAPPSTAT = DESCRIPTOR.message_types_by_name['IpLayerAppStat']
_IPLAYERNETWORKBUCKET = DESCRIPTOR.message_types_by_name['IpLayerNetworkBucket']
_IPLAYERNETWORKSTAT = DESCRIPTOR.message_types_by_name['IpLayerNetworkStat']
_KEYTOPACKAGENAMEMAPPING = DESCRIPTOR.message_types_by_name['KeyToPackageNameMapping']
_PACKAGEINFO = DESCRIPTOR.message_types_by_name['PackageInfo']
_PAYLOADLEVELAPPSTAT = DESCRIPTOR.message_types_by_name['PayloadLevelAppStat']
_STATCOUNTERS = DESCRIPTOR.message_types_by_name['StatCounters']
_USAGESTATSEXTENSIONPROTO = DESCRIPTOR.message_types_by_name['UsageStatsExtensionProto']
_MODIFYLIBRARYREQUEST = DESCRIPTOR.message_types_by_name['ModifyLibraryRequest']
_URLREQUESTWRAPPER = DESCRIPTOR.message_types_by_name['UrlRequestWrapper']
_DEVELOPERAPPSREQUEST = DESCRIPTOR.message_types_by_name['DeveloperAppsRequest']
_DEVELOPERIDCONTAINER = DESCRIPTOR.message_types_by_name['DeveloperIdContainer']
AndroidAppDeliveryData = _reflection.GeneratedProtocolMessageType('AndroidAppDeliveryData', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDAPPDELIVERYDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidAppDeliveryData)
})
_sym_db.RegisterMessage(AndroidAppDeliveryData)

Split = _reflection.GeneratedProtocolMessageType('Split', (_message.Message,), {
    'DESCRIPTOR': _SPLIT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Split)
})
_sym_db.RegisterMessage(Split)

AndroidAppPatchData = _reflection.GeneratedProtocolMessageType('AndroidAppPatchData', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDAPPPATCHDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidAppPatchData)
})
_sym_db.RegisterMessage(AndroidAppPatchData)

AppFileMetadata = _reflection.GeneratedProtocolMessageType('AppFileMetadata', (_message.Message,), {
    'DESCRIPTOR': _APPFILEMETADATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AppFileMetadata)
})
_sym_db.RegisterMessage(AppFileMetadata)

EncryptionParams = _reflection.GeneratedProtocolMessageType('EncryptionParams', (_message.Message,), {
    'DESCRIPTOR': _ENCRYPTIONPARAMS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:EncryptionParams)
})
_sym_db.RegisterMessage(EncryptionParams)

HttpCookie = _reflection.GeneratedProtocolMessageType('HttpCookie', (_message.Message,), {
    'DESCRIPTOR': _HTTPCOOKIE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:HttpCookie)
})
_sym_db.RegisterMessage(HttpCookie)

Address = _reflection.GeneratedProtocolMessageType('Address', (_message.Message,), {
    'DESCRIPTOR': _ADDRESS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Address)
})
_sym_db.RegisterMessage(Address)

BookAuthor = _reflection.GeneratedProtocolMessageType('BookAuthor', (_message.Message,), {
    'DESCRIPTOR': _BOOKAUTHOR,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BookAuthor)
})
_sym_db.RegisterMessage(BookAuthor)

BookDetails = _reflection.GeneratedProtocolMessageType('BookDetails', (_message.Message,), {

    'Identifier': _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {
        'DESCRIPTOR': _BOOKDETAILS_IDENTIFIER,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:BookDetails.Identifier)
    })
    ,
    'DESCRIPTOR': _BOOKDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BookDetails)
})
_sym_db.RegisterMessage(BookDetails)
_sym_db.RegisterMessage(BookDetails.Identifier)

BookSubject = _reflection.GeneratedProtocolMessageType('BookSubject', (_message.Message,), {
    'DESCRIPTOR': _BOOKSUBJECT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BookSubject)
})
_sym_db.RegisterMessage(BookSubject)

BrowseLink = _reflection.GeneratedProtocolMessageType('BrowseLink', (_message.Message,), {
    'DESCRIPTOR': _BROWSELINK,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BrowseLink)
})
_sym_db.RegisterMessage(BrowseLink)

UnknownCategoryContainer = _reflection.GeneratedProtocolMessageType('UnknownCategoryContainer', (_message.Message,), {
    'DESCRIPTOR': _UNKNOWNCATEGORYCONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UnknownCategoryContainer)
})
_sym_db.RegisterMessage(UnknownCategoryContainer)

CategoryIdContainer = _reflection.GeneratedProtocolMessageType('CategoryIdContainer', (_message.Message,), {
    'DESCRIPTOR': _CATEGORYIDCONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CategoryIdContainer)
})
_sym_db.RegisterMessage(CategoryIdContainer)

BrowseResponse = _reflection.GeneratedProtocolMessageType('BrowseResponse', (_message.Message,), {
    'DESCRIPTOR': _BROWSERESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BrowseResponse)
})
_sym_db.RegisterMessage(BrowseResponse)

CategoryContainer = _reflection.GeneratedProtocolMessageType('CategoryContainer', (_message.Message,), {
    'DESCRIPTOR': _CATEGORYCONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CategoryContainer)
})
_sym_db.RegisterMessage(CategoryContainer)

AddressChallenge = _reflection.GeneratedProtocolMessageType('AddressChallenge', (_message.Message,), {
    'DESCRIPTOR': _ADDRESSCHALLENGE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AddressChallenge)
})
_sym_db.RegisterMessage(AddressChallenge)

AuthenticationChallenge = _reflection.GeneratedProtocolMessageType('AuthenticationChallenge', (_message.Message,), {
    'DESCRIPTOR': _AUTHENTICATIONCHALLENGE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AuthenticationChallenge)
})
_sym_db.RegisterMessage(AuthenticationChallenge)

BuyResponse = _reflection.GeneratedProtocolMessageType('BuyResponse', (_message.Message,), {

    'CheckoutInfo': _reflection.GeneratedProtocolMessageType('CheckoutInfo', (_message.Message,), {

        'CheckoutOption': _reflection.GeneratedProtocolMessageType('CheckoutOption', (_message.Message,), {
            'DESCRIPTOR': _BUYRESPONSE_CHECKOUTINFO_CHECKOUTOPTION,
            '__module__': 'googleplay_pb2'
            # @@protoc_insertion_point(class_scope:BuyResponse.CheckoutInfo.CheckoutOption)
        })
        ,
        'DESCRIPTOR': _BUYRESPONSE_CHECKOUTINFO,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:BuyResponse.CheckoutInfo)
    })
    ,
    'DESCRIPTOR': _BUYRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BuyResponse)
})
_sym_db.RegisterMessage(BuyResponse)
_sym_db.RegisterMessage(BuyResponse.CheckoutInfo)
_sym_db.RegisterMessage(BuyResponse.CheckoutInfo.CheckoutOption)

Challenge = _reflection.GeneratedProtocolMessageType('Challenge', (_message.Message,), {
    'DESCRIPTOR': _CHALLENGE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Challenge)
})
_sym_db.RegisterMessage(Challenge)

FormCheckbox = _reflection.GeneratedProtocolMessageType('FormCheckbox', (_message.Message,), {
    'DESCRIPTOR': _FORMCHECKBOX,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:FormCheckbox)
})
_sym_db.RegisterMessage(FormCheckbox)

LineItem = _reflection.GeneratedProtocolMessageType('LineItem', (_message.Message,), {
    'DESCRIPTOR': _LINEITEM,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LineItem)
})
_sym_db.RegisterMessage(LineItem)

Money = _reflection.GeneratedProtocolMessageType('Money', (_message.Message,), {
    'DESCRIPTOR': _MONEY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Money)
})
_sym_db.RegisterMessage(Money)

PurchaseNotificationResponse = _reflection.GeneratedProtocolMessageType('PurchaseNotificationResponse',
                                                                        (_message.Message,), {
                                                                            'DESCRIPTOR': _PURCHASENOTIFICATIONRESPONSE,
                                                                            '__module__': 'googleplay_pb2'
                                                                            # @@protoc_insertion_point(class_scope:PurchaseNotificationResponse)
                                                                        })
_sym_db.RegisterMessage(PurchaseNotificationResponse)

PurchaseStatusResponse = _reflection.GeneratedProtocolMessageType('PurchaseStatusResponse', (_message.Message,), {
    'DESCRIPTOR': _PURCHASESTATUSRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PurchaseStatusResponse)
})
_sym_db.RegisterMessage(PurchaseStatusResponse)

DeliveryResponse = _reflection.GeneratedProtocolMessageType('DeliveryResponse', (_message.Message,), {
    'DESCRIPTOR': _DELIVERYRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DeliveryResponse)
})
_sym_db.RegisterMessage(DeliveryResponse)

Docid = _reflection.GeneratedProtocolMessageType('Docid', (_message.Message,), {
    'DESCRIPTOR': _DOCID,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Docid)
})
_sym_db.RegisterMessage(Docid)

Install = _reflection.GeneratedProtocolMessageType('Install', (_message.Message,), {
    'DESCRIPTOR': _INSTALL,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Install)
})
_sym_db.RegisterMessage(Install)

Offer = _reflection.GeneratedProtocolMessageType('Offer', (_message.Message,), {
    'DESCRIPTOR': _OFFER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Offer)
})
_sym_db.RegisterMessage(Offer)

OwnershipInfo = _reflection.GeneratedProtocolMessageType('OwnershipInfo', (_message.Message,), {
    'DESCRIPTOR': _OWNERSHIPINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:OwnershipInfo)
})
_sym_db.RegisterMessage(OwnershipInfo)

RentalTerms = _reflection.GeneratedProtocolMessageType('RentalTerms', (_message.Message,), {
    'DESCRIPTOR': _RENTALTERMS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RentalTerms)
})
_sym_db.RegisterMessage(RentalTerms)

SubscriptionTerms = _reflection.GeneratedProtocolMessageType('SubscriptionTerms', (_message.Message,), {
    'DESCRIPTOR': _SUBSCRIPTIONTERMS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SubscriptionTerms)
})
_sym_db.RegisterMessage(SubscriptionTerms)

TimePeriod = _reflection.GeneratedProtocolMessageType('TimePeriod', (_message.Message,), {
    'DESCRIPTOR': _TIMEPERIOD,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TimePeriod)
})
_sym_db.RegisterMessage(TimePeriod)

BillingAddressSpec = _reflection.GeneratedProtocolMessageType('BillingAddressSpec', (_message.Message,), {
    'DESCRIPTOR': _BILLINGADDRESSSPEC,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BillingAddressSpec)
})
_sym_db.RegisterMessage(BillingAddressSpec)

CarrierBillingCredentials = _reflection.GeneratedProtocolMessageType('CarrierBillingCredentials', (_message.Message,), {
    'DESCRIPTOR': _CARRIERBILLINGCREDENTIALS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CarrierBillingCredentials)
})
_sym_db.RegisterMessage(CarrierBillingCredentials)

CarrierBillingInstrument = _reflection.GeneratedProtocolMessageType('CarrierBillingInstrument', (_message.Message,), {
    'DESCRIPTOR': _CARRIERBILLINGINSTRUMENT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CarrierBillingInstrument)
})
_sym_db.RegisterMessage(CarrierBillingInstrument)

CarrierBillingInstrumentStatus = _reflection.GeneratedProtocolMessageType('CarrierBillingInstrumentStatus',
                                                                          (_message.Message,), {
                                                                              'DESCRIPTOR': _CARRIERBILLINGINSTRUMENTSTATUS,
                                                                              '__module__': 'googleplay_pb2'
                                                                              # @@protoc_insertion_point(class_scope:CarrierBillingInstrumentStatus)
                                                                          })
_sym_db.RegisterMessage(CarrierBillingInstrumentStatus)

CarrierTos = _reflection.GeneratedProtocolMessageType('CarrierTos', (_message.Message,), {
    'DESCRIPTOR': _CARRIERTOS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CarrierTos)
})
_sym_db.RegisterMessage(CarrierTos)

CarrierTosEntry = _reflection.GeneratedProtocolMessageType('CarrierTosEntry', (_message.Message,), {
    'DESCRIPTOR': _CARRIERTOSENTRY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CarrierTosEntry)
})
_sym_db.RegisterMessage(CarrierTosEntry)

CreditCardInstrument = _reflection.GeneratedProtocolMessageType('CreditCardInstrument', (_message.Message,), {
    'DESCRIPTOR': _CREDITCARDINSTRUMENT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CreditCardInstrument)
})
_sym_db.RegisterMessage(CreditCardInstrument)

EfeParam = _reflection.GeneratedProtocolMessageType('EfeParam', (_message.Message,), {
    'DESCRIPTOR': _EFEPARAM,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:EfeParam)
})
_sym_db.RegisterMessage(EfeParam)

InputValidationError = _reflection.GeneratedProtocolMessageType('InputValidationError', (_message.Message,), {
    'DESCRIPTOR': _INPUTVALIDATIONERROR,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:InputValidationError)
})
_sym_db.RegisterMessage(InputValidationError)

Instrument = _reflection.GeneratedProtocolMessageType('Instrument', (_message.Message,), {
    'DESCRIPTOR': _INSTRUMENT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Instrument)
})
_sym_db.RegisterMessage(Instrument)

PasswordPrompt = _reflection.GeneratedProtocolMessageType('PasswordPrompt', (_message.Message,), {
    'DESCRIPTOR': _PASSWORDPROMPT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PasswordPrompt)
})
_sym_db.RegisterMessage(PasswordPrompt)

ContainerMetadata = _reflection.GeneratedProtocolMessageType('ContainerMetadata', (_message.Message,), {
    'DESCRIPTOR': _CONTAINERMETADATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ContainerMetadata)
})
_sym_db.RegisterMessage(ContainerMetadata)

DebugInfo = _reflection.GeneratedProtocolMessageType('DebugInfo', (_message.Message,), {

    'Timing': _reflection.GeneratedProtocolMessageType('Timing', (_message.Message,), {
        'DESCRIPTOR': _DEBUGINFO_TIMING,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:DebugInfo.Timing)
    })
    ,
    'DESCRIPTOR': _DEBUGINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DebugInfo)
})
_sym_db.RegisterMessage(DebugInfo)
_sym_db.RegisterMessage(DebugInfo.Timing)

BulkDetailsEntry = _reflection.GeneratedProtocolMessageType('BulkDetailsEntry', (_message.Message,), {
    'DESCRIPTOR': _BULKDETAILSENTRY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BulkDetailsEntry)
})
_sym_db.RegisterMessage(BulkDetailsEntry)

BulkDetailsRequest = _reflection.GeneratedProtocolMessageType('BulkDetailsRequest', (_message.Message,), {
    'DESCRIPTOR': _BULKDETAILSREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BulkDetailsRequest)
})
_sym_db.RegisterMessage(BulkDetailsRequest)

BulkDetailsResponse = _reflection.GeneratedProtocolMessageType('BulkDetailsResponse', (_message.Message,), {
    'DESCRIPTOR': _BULKDETAILSRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BulkDetailsResponse)
})
_sym_db.RegisterMessage(BulkDetailsResponse)

DetailsResponse = _reflection.GeneratedProtocolMessageType('DetailsResponse', (_message.Message,), {
    'DESCRIPTOR': _DETAILSRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DetailsResponse)
})
_sym_db.RegisterMessage(DetailsResponse)

Badge = _reflection.GeneratedProtocolMessageType('Badge', (_message.Message,), {
    'DESCRIPTOR': _BADGE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Badge)
})
_sym_db.RegisterMessage(Badge)

BadgeContainer1 = _reflection.GeneratedProtocolMessageType('BadgeContainer1', (_message.Message,), {
    'DESCRIPTOR': _BADGECONTAINER1,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BadgeContainer1)
})
_sym_db.RegisterMessage(BadgeContainer1)

BadgeContainer2 = _reflection.GeneratedProtocolMessageType('BadgeContainer2', (_message.Message,), {
    'DESCRIPTOR': _BADGECONTAINER2,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BadgeContainer2)
})
_sym_db.RegisterMessage(BadgeContainer2)

BadgeLinkContainer = _reflection.GeneratedProtocolMessageType('BadgeLinkContainer', (_message.Message,), {
    'DESCRIPTOR': _BADGELINKCONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BadgeLinkContainer)
})
_sym_db.RegisterMessage(BadgeLinkContainer)

Features = _reflection.GeneratedProtocolMessageType('Features', (_message.Message,), {
    'DESCRIPTOR': _FEATURES,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Features)
})
_sym_db.RegisterMessage(Features)

Feature = _reflection.GeneratedProtocolMessageType('Feature', (_message.Message,), {
    'DESCRIPTOR': _FEATURE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Feature)
})
_sym_db.RegisterMessage(Feature)

DeviceConfigurationProto = _reflection.GeneratedProtocolMessageType('DeviceConfigurationProto', (_message.Message,), {
    'DESCRIPTOR': _DEVICECONFIGURATIONPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DeviceConfigurationProto)
})
_sym_db.RegisterMessage(DeviceConfigurationProto)

Document = _reflection.GeneratedProtocolMessageType('Document', (_message.Message,), {
    'DESCRIPTOR': _DOCUMENT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Document)
})
_sym_db.RegisterMessage(Document)

DocumentVariant = _reflection.GeneratedProtocolMessageType('DocumentVariant', (_message.Message,), {
    'DESCRIPTOR': _DOCUMENTVARIANT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DocumentVariant)
})
_sym_db.RegisterMessage(DocumentVariant)

Image = _reflection.GeneratedProtocolMessageType('Image', (_message.Message,), {

    'Dimension': _reflection.GeneratedProtocolMessageType('Dimension', (_message.Message,), {
        'DESCRIPTOR': _IMAGE_DIMENSION,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:Image.Dimension)
    })
    ,

    'Citation': _reflection.GeneratedProtocolMessageType('Citation', (_message.Message,), {
        'DESCRIPTOR': _IMAGE_CITATION,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:Image.Citation)
    })
    ,
    'DESCRIPTOR': _IMAGE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Image)
})
_sym_db.RegisterMessage(Image)
_sym_db.RegisterMessage(Image.Dimension)
_sym_db.RegisterMessage(Image.Citation)

TranslatedText = _reflection.GeneratedProtocolMessageType('TranslatedText', (_message.Message,), {
    'DESCRIPTOR': _TRANSLATEDTEXT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TranslatedText)
})
_sym_db.RegisterMessage(TranslatedText)

PlusOneData = _reflection.GeneratedProtocolMessageType('PlusOneData', (_message.Message,), {
    'DESCRIPTOR': _PLUSONEDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PlusOneData)
})
_sym_db.RegisterMessage(PlusOneData)

PlusPerson = _reflection.GeneratedProtocolMessageType('PlusPerson', (_message.Message,), {
    'DESCRIPTOR': _PLUSPERSON,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PlusPerson)
})
_sym_db.RegisterMessage(PlusPerson)

AlbumDetails = _reflection.GeneratedProtocolMessageType('AlbumDetails', (_message.Message,), {
    'DESCRIPTOR': _ALBUMDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AlbumDetails)
})
_sym_db.RegisterMessage(AlbumDetails)

AppDetails = _reflection.GeneratedProtocolMessageType('AppDetails', (_message.Message,), {
    'DESCRIPTOR': _APPDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AppDetails)
})
_sym_db.RegisterMessage(AppDetails)

Dependencies = _reflection.GeneratedProtocolMessageType('Dependencies', (_message.Message,), {
    'DESCRIPTOR': _DEPENDENCIES,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Dependencies)
})
_sym_db.RegisterMessage(Dependencies)

Dependency = _reflection.GeneratedProtocolMessageType('Dependency', (_message.Message,), {
    'DESCRIPTOR': _DEPENDENCY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Dependency)
})
_sym_db.RegisterMessage(Dependency)

TestingProgramInfo = _reflection.GeneratedProtocolMessageType('TestingProgramInfo', (_message.Message,), {
    'DESCRIPTOR': _TESTINGPROGRAMINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TestingProgramInfo)
})
_sym_db.RegisterMessage(TestingProgramInfo)

EarlyAccessInfo = _reflection.GeneratedProtocolMessageType('EarlyAccessInfo', (_message.Message,), {
    'DESCRIPTOR': _EARLYACCESSINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:EarlyAccessInfo)
})
_sym_db.RegisterMessage(EarlyAccessInfo)

ArtistDetails = _reflection.GeneratedProtocolMessageType('ArtistDetails', (_message.Message,), {
    'DESCRIPTOR': _ARTISTDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ArtistDetails)
})
_sym_db.RegisterMessage(ArtistDetails)

ArtistExternalLinks = _reflection.GeneratedProtocolMessageType('ArtistExternalLinks', (_message.Message,), {
    'DESCRIPTOR': _ARTISTEXTERNALLINKS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ArtistExternalLinks)
})
_sym_db.RegisterMessage(ArtistExternalLinks)

DocumentDetails = _reflection.GeneratedProtocolMessageType('DocumentDetails', (_message.Message,), {
    'DESCRIPTOR': _DOCUMENTDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DocumentDetails)
})
_sym_db.RegisterMessage(DocumentDetails)

FileMetadata = _reflection.GeneratedProtocolMessageType('FileMetadata', (_message.Message,), {
    'DESCRIPTOR': _FILEMETADATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:FileMetadata)
})
_sym_db.RegisterMessage(FileMetadata)

MagazineDetails = _reflection.GeneratedProtocolMessageType('MagazineDetails', (_message.Message,), {
    'DESCRIPTOR': _MAGAZINEDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:MagazineDetails)
})
_sym_db.RegisterMessage(MagazineDetails)

MusicDetails = _reflection.GeneratedProtocolMessageType('MusicDetails', (_message.Message,), {
    'DESCRIPTOR': _MUSICDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:MusicDetails)
})
_sym_db.RegisterMessage(MusicDetails)

SongDetails = _reflection.GeneratedProtocolMessageType('SongDetails', (_message.Message,), {
    'DESCRIPTOR': _SONGDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SongDetails)
})
_sym_db.RegisterMessage(SongDetails)

SubscriptionDetails = _reflection.GeneratedProtocolMessageType('SubscriptionDetails', (_message.Message,), {
    'DESCRIPTOR': _SUBSCRIPTIONDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SubscriptionDetails)
})
_sym_db.RegisterMessage(SubscriptionDetails)

Trailer = _reflection.GeneratedProtocolMessageType('Trailer', (_message.Message,), {
    'DESCRIPTOR': _TRAILER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Trailer)
})
_sym_db.RegisterMessage(Trailer)

TvEpisodeDetails = _reflection.GeneratedProtocolMessageType('TvEpisodeDetails', (_message.Message,), {
    'DESCRIPTOR': _TVEPISODEDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TvEpisodeDetails)
})
_sym_db.RegisterMessage(TvEpisodeDetails)

TvSeasonDetails = _reflection.GeneratedProtocolMessageType('TvSeasonDetails', (_message.Message,), {
    'DESCRIPTOR': _TVSEASONDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TvSeasonDetails)
})
_sym_db.RegisterMessage(TvSeasonDetails)

TvShowDetails = _reflection.GeneratedProtocolMessageType('TvShowDetails', (_message.Message,), {
    'DESCRIPTOR': _TVSHOWDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TvShowDetails)
})
_sym_db.RegisterMessage(TvShowDetails)

VideoCredit = _reflection.GeneratedProtocolMessageType('VideoCredit', (_message.Message,), {
    'DESCRIPTOR': _VIDEOCREDIT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:VideoCredit)
})
_sym_db.RegisterMessage(VideoCredit)

VideoDetails = _reflection.GeneratedProtocolMessageType('VideoDetails', (_message.Message,), {
    'DESCRIPTOR': _VIDEODETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:VideoDetails)
})
_sym_db.RegisterMessage(VideoDetails)

VideoRentalTerm = _reflection.GeneratedProtocolMessageType('VideoRentalTerm', (_message.Message,), {

    'Term': _reflection.GeneratedProtocolMessageType('Term', (_message.Message,), {
        'DESCRIPTOR': _VIDEORENTALTERM_TERM,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:VideoRentalTerm.Term)
    })
    ,
    'DESCRIPTOR': _VIDEORENTALTERM,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:VideoRentalTerm)
})
_sym_db.RegisterMessage(VideoRentalTerm)
_sym_db.RegisterMessage(VideoRentalTerm.Term)

Bucket = _reflection.GeneratedProtocolMessageType('Bucket', (_message.Message,), {
    'DESCRIPTOR': _BUCKET,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Bucket)
})
_sym_db.RegisterMessage(Bucket)

ListResponse = _reflection.GeneratedProtocolMessageType('ListResponse', (_message.Message,), {
    'DESCRIPTOR': _LISTRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ListResponse)
})
_sym_db.RegisterMessage(ListResponse)

DocV1 = _reflection.GeneratedProtocolMessageType('DocV1', (_message.Message,), {
    'DESCRIPTOR': _DOCV1,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DocV1)
})
_sym_db.RegisterMessage(DocV1)

DocV2 = _reflection.GeneratedProtocolMessageType('DocV2', (_message.Message,), {
    'DESCRIPTOR': _DOCV2,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DocV2)
})
_sym_db.RegisterMessage(DocV2)

Unknown25 = _reflection.GeneratedProtocolMessageType('Unknown25', (_message.Message,), {
    'DESCRIPTOR': _UNKNOWN25,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Unknown25)
})
_sym_db.RegisterMessage(Unknown25)

Unknown25Item = _reflection.GeneratedProtocolMessageType('Unknown25Item', (_message.Message,), {
    'DESCRIPTOR': _UNKNOWN25ITEM,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Unknown25Item)
})
_sym_db.RegisterMessage(Unknown25Item)

Unknown25Container = _reflection.GeneratedProtocolMessageType('Unknown25Container', (_message.Message,), {
    'DESCRIPTOR': _UNKNOWN25CONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Unknown25Container)
})
_sym_db.RegisterMessage(Unknown25Container)

RelatedLinks = _reflection.GeneratedProtocolMessageType('RelatedLinks', (_message.Message,), {
    'DESCRIPTOR': _RELATEDLINKS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RelatedLinks)
})
_sym_db.RegisterMessage(RelatedLinks)

RelatedLinksUnknown1 = _reflection.GeneratedProtocolMessageType('RelatedLinksUnknown1', (_message.Message,), {
    'DESCRIPTOR': _RELATEDLINKSUNKNOWN1,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RelatedLinksUnknown1)
})
_sym_db.RegisterMessage(RelatedLinksUnknown1)

RelatedLinksUnknown2 = _reflection.GeneratedProtocolMessageType('RelatedLinksUnknown2', (_message.Message,), {
    'DESCRIPTOR': _RELATEDLINKSUNKNOWN2,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RelatedLinksUnknown2)
})
_sym_db.RegisterMessage(RelatedLinksUnknown2)

Rated = _reflection.GeneratedProtocolMessageType('Rated', (_message.Message,), {
    'DESCRIPTOR': _RATED,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Rated)
})
_sym_db.RegisterMessage(Rated)

RelatedLink = _reflection.GeneratedProtocolMessageType('RelatedLink', (_message.Message,), {
    'DESCRIPTOR': _RELATEDLINK,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RelatedLink)
})
_sym_db.RegisterMessage(RelatedLink)

CategoryInfo = _reflection.GeneratedProtocolMessageType('CategoryInfo', (_message.Message,), {
    'DESCRIPTOR': _CATEGORYINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CategoryInfo)
})
_sym_db.RegisterMessage(CategoryInfo)

EncryptedSubscriberInfo = _reflection.GeneratedProtocolMessageType('EncryptedSubscriberInfo', (_message.Message,), {
    'DESCRIPTOR': _ENCRYPTEDSUBSCRIBERINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:EncryptedSubscriberInfo)
})
_sym_db.RegisterMessage(EncryptedSubscriberInfo)

Availability = _reflection.GeneratedProtocolMessageType('Availability', (_message.Message,), {

    'PerDeviceAvailabilityRestriction': _reflection.GeneratedProtocolMessageType('PerDeviceAvailabilityRestriction',
                                                                                 (_message.Message,), {
                                                                                     'DESCRIPTOR': _AVAILABILITY_PERDEVICEAVAILABILITYRESTRICTION,
                                                                                     '__module__': 'googleplay_pb2'
                                                                                     # @@protoc_insertion_point(class_scope:Availability.PerDeviceAvailabilityRestriction)
                                                                                 })
    ,
    'DESCRIPTOR': _AVAILABILITY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Availability)
})
_sym_db.RegisterMessage(Availability)
_sym_db.RegisterMessage(Availability.PerDeviceAvailabilityRestriction)

FilterEvaluationInfo = _reflection.GeneratedProtocolMessageType('FilterEvaluationInfo', (_message.Message,), {
    'DESCRIPTOR': _FILTEREVALUATIONINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:FilterEvaluationInfo)
})
_sym_db.RegisterMessage(FilterEvaluationInfo)

Rule = _reflection.GeneratedProtocolMessageType('Rule', (_message.Message,), {
    'DESCRIPTOR': _RULE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Rule)
})
_sym_db.RegisterMessage(Rule)

RuleEvaluation = _reflection.GeneratedProtocolMessageType('RuleEvaluation', (_message.Message,), {
    'DESCRIPTOR': _RULEEVALUATION,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RuleEvaluation)
})
_sym_db.RegisterMessage(RuleEvaluation)

LibraryAppDetails = _reflection.GeneratedProtocolMessageType('LibraryAppDetails', (_message.Message,), {
    'DESCRIPTOR': _LIBRARYAPPDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LibraryAppDetails)
})
_sym_db.RegisterMessage(LibraryAppDetails)

LibraryInAppDetails = _reflection.GeneratedProtocolMessageType('LibraryInAppDetails', (_message.Message,), {
    'DESCRIPTOR': _LIBRARYINAPPDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LibraryInAppDetails)
})
_sym_db.RegisterMessage(LibraryInAppDetails)

LibraryMutation = _reflection.GeneratedProtocolMessageType('LibraryMutation', (_message.Message,), {
    'DESCRIPTOR': _LIBRARYMUTATION,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LibraryMutation)
})
_sym_db.RegisterMessage(LibraryMutation)

LibrarySubscriptionDetails = _reflection.GeneratedProtocolMessageType('LibrarySubscriptionDetails', (_message.Message,),
                                                                      {
                                                                          'DESCRIPTOR': _LIBRARYSUBSCRIPTIONDETAILS,
                                                                          '__module__': 'googleplay_pb2'
                                                                          # @@protoc_insertion_point(class_scope:LibrarySubscriptionDetails)
                                                                      })
_sym_db.RegisterMessage(LibrarySubscriptionDetails)

LibraryUpdate = _reflection.GeneratedProtocolMessageType('LibraryUpdate', (_message.Message,), {
    'DESCRIPTOR': _LIBRARYUPDATE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LibraryUpdate)
})
_sym_db.RegisterMessage(LibraryUpdate)

AndroidAppNotificationData = _reflection.GeneratedProtocolMessageType('AndroidAppNotificationData', (_message.Message,),
                                                                      {
                                                                          'DESCRIPTOR': _ANDROIDAPPNOTIFICATIONDATA,
                                                                          '__module__': 'googleplay_pb2'
                                                                          # @@protoc_insertion_point(class_scope:AndroidAppNotificationData)
                                                                      })
_sym_db.RegisterMessage(AndroidAppNotificationData)

InAppNotificationData = _reflection.GeneratedProtocolMessageType('InAppNotificationData', (_message.Message,), {
    'DESCRIPTOR': _INAPPNOTIFICATIONDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:InAppNotificationData)
})
_sym_db.RegisterMessage(InAppNotificationData)

LibraryDirtyData = _reflection.GeneratedProtocolMessageType('LibraryDirtyData', (_message.Message,), {
    'DESCRIPTOR': _LIBRARYDIRTYDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LibraryDirtyData)
})
_sym_db.RegisterMessage(LibraryDirtyData)

Notification = _reflection.GeneratedProtocolMessageType('Notification', (_message.Message,), {
    'DESCRIPTOR': _NOTIFICATION,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Notification)
})
_sym_db.RegisterMessage(Notification)

PurchaseDeclinedData = _reflection.GeneratedProtocolMessageType('PurchaseDeclinedData', (_message.Message,), {
    'DESCRIPTOR': _PURCHASEDECLINEDDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PurchaseDeclinedData)
})
_sym_db.RegisterMessage(PurchaseDeclinedData)

PurchaseRemovalData = _reflection.GeneratedProtocolMessageType('PurchaseRemovalData', (_message.Message,), {
    'DESCRIPTOR': _PURCHASEREMOVALDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PurchaseRemovalData)
})
_sym_db.RegisterMessage(PurchaseRemovalData)

UserNotificationData = _reflection.GeneratedProtocolMessageType('UserNotificationData', (_message.Message,), {
    'DESCRIPTOR': _USERNOTIFICATIONDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UserNotificationData)
})
_sym_db.RegisterMessage(UserNotificationData)

AggregateRating = _reflection.GeneratedProtocolMessageType('AggregateRating', (_message.Message,), {
    'DESCRIPTOR': _AGGREGATERATING,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AggregateRating)
})
_sym_db.RegisterMessage(AggregateRating)

AcceptTosResponse = _reflection.GeneratedProtocolMessageType('AcceptTosResponse', (_message.Message,), {
    'DESCRIPTOR': _ACCEPTTOSRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AcceptTosResponse)
})
_sym_db.RegisterMessage(AcceptTosResponse)

CarrierBillingConfig = _reflection.GeneratedProtocolMessageType('CarrierBillingConfig', (_message.Message,), {
    'DESCRIPTOR': _CARRIERBILLINGCONFIG,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CarrierBillingConfig)
})
_sym_db.RegisterMessage(CarrierBillingConfig)

BillingConfig = _reflection.GeneratedProtocolMessageType('BillingConfig', (_message.Message,), {
    'DESCRIPTOR': _BILLINGCONFIG,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:BillingConfig)
})
_sym_db.RegisterMessage(BillingConfig)

CorpusMetadata = _reflection.GeneratedProtocolMessageType('CorpusMetadata', (_message.Message,), {
    'DESCRIPTOR': _CORPUSMETADATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CorpusMetadata)
})
_sym_db.RegisterMessage(CorpusMetadata)

Experiments = _reflection.GeneratedProtocolMessageType('Experiments', (_message.Message,), {
    'DESCRIPTOR': _EXPERIMENTS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Experiments)
})
_sym_db.RegisterMessage(Experiments)

SelfUpdateConfig = _reflection.GeneratedProtocolMessageType('SelfUpdateConfig', (_message.Message,), {
    'DESCRIPTOR': _SELFUPDATECONFIG,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SelfUpdateConfig)
})
_sym_db.RegisterMessage(SelfUpdateConfig)

TocResponse = _reflection.GeneratedProtocolMessageType('TocResponse', (_message.Message,), {
    'DESCRIPTOR': _TOCRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TocResponse)
})
_sym_db.RegisterMessage(TocResponse)

Payload = _reflection.GeneratedProtocolMessageType('Payload', (_message.Message,), {
    'DESCRIPTOR': _PAYLOAD,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Payload)
})
_sym_db.RegisterMessage(Payload)

PreFetch = _reflection.GeneratedProtocolMessageType('PreFetch', (_message.Message,), {
    'DESCRIPTOR': _PREFETCH,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PreFetch)
})
_sym_db.RegisterMessage(PreFetch)

ServerMetadata = _reflection.GeneratedProtocolMessageType('ServerMetadata', (_message.Message,), {
    'DESCRIPTOR': _SERVERMETADATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ServerMetadata)
})
_sym_db.RegisterMessage(ServerMetadata)

Targets = _reflection.GeneratedProtocolMessageType('Targets', (_message.Message,), {
    'DESCRIPTOR': _TARGETS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Targets)
})
_sym_db.RegisterMessage(Targets)

ServerCookie = _reflection.GeneratedProtocolMessageType('ServerCookie', (_message.Message,), {
    'DESCRIPTOR': _SERVERCOOKIE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ServerCookie)
})
_sym_db.RegisterMessage(ServerCookie)

ServerCookies = _reflection.GeneratedProtocolMessageType('ServerCookies', (_message.Message,), {
    'DESCRIPTOR': _SERVERCOOKIES,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ServerCookies)
})
_sym_db.RegisterMessage(ServerCookies)

ResponseWrapper = _reflection.GeneratedProtocolMessageType('ResponseWrapper', (_message.Message,), {
    'DESCRIPTOR': _RESPONSEWRAPPER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ResponseWrapper)
})
_sym_db.RegisterMessage(ResponseWrapper)

ResponseWrapperApi = _reflection.GeneratedProtocolMessageType('ResponseWrapperApi', (_message.Message,), {
    'DESCRIPTOR': _RESPONSEWRAPPERAPI,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ResponseWrapperApi)
})
_sym_db.RegisterMessage(ResponseWrapperApi)

PayloadApi = _reflection.GeneratedProtocolMessageType('PayloadApi', (_message.Message,), {
    'DESCRIPTOR': _PAYLOADAPI,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PayloadApi)
})
_sym_db.RegisterMessage(PayloadApi)

UserProfileResponse = _reflection.GeneratedProtocolMessageType('UserProfileResponse', (_message.Message,), {
    'DESCRIPTOR': _USERPROFILERESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UserProfileResponse)
})
_sym_db.RegisterMessage(UserProfileResponse)

ServerCommands = _reflection.GeneratedProtocolMessageType('ServerCommands', (_message.Message,), {
    'DESCRIPTOR': _SERVERCOMMANDS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ServerCommands)
})
_sym_db.RegisterMessage(ServerCommands)

GetReviewsResponse = _reflection.GeneratedProtocolMessageType('GetReviewsResponse', (_message.Message,), {
    'DESCRIPTOR': _GETREVIEWSRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:GetReviewsResponse)
})
_sym_db.RegisterMessage(GetReviewsResponse)

Review = _reflection.GeneratedProtocolMessageType('Review', (_message.Message,), {
    'DESCRIPTOR': _REVIEW,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:Review)
})
_sym_db.RegisterMessage(Review)

ReviewAuthor = _reflection.GeneratedProtocolMessageType('ReviewAuthor', (_message.Message,), {
    'DESCRIPTOR': _REVIEWAUTHOR,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ReviewAuthor)
})
_sym_db.RegisterMessage(ReviewAuthor)

UserProfile = _reflection.GeneratedProtocolMessageType('UserProfile', (_message.Message,), {
    'DESCRIPTOR': _USERPROFILE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UserProfile)
})
_sym_db.RegisterMessage(UserProfile)

ReviewResponse = _reflection.GeneratedProtocolMessageType('ReviewResponse', (_message.Message,), {
    'DESCRIPTOR': _REVIEWRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ReviewResponse)
})
_sym_db.RegisterMessage(ReviewResponse)

RelatedSearch = _reflection.GeneratedProtocolMessageType('RelatedSearch', (_message.Message,), {
    'DESCRIPTOR': _RELATEDSEARCH,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:RelatedSearch)
})
_sym_db.RegisterMessage(RelatedSearch)

SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {
    'DESCRIPTOR': _SEARCHRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SearchResponse)
})
_sym_db.RegisterMessage(SearchResponse)

SearchSuggestResponse = _reflection.GeneratedProtocolMessageType('SearchSuggestResponse', (_message.Message,), {
    'DESCRIPTOR': _SEARCHSUGGESTRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SearchSuggestResponse)
})
_sym_db.RegisterMessage(SearchSuggestResponse)

SearchSuggestEntry = _reflection.GeneratedProtocolMessageType('SearchSuggestEntry', (_message.Message,), {

    'ImageContainer': _reflection.GeneratedProtocolMessageType('ImageContainer', (_message.Message,), {
        'DESCRIPTOR': _SEARCHSUGGESTENTRY_IMAGECONTAINER,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:SearchSuggestEntry.ImageContainer)
    })
    ,

    'PackageNameContainer': _reflection.GeneratedProtocolMessageType('PackageNameContainer', (_message.Message,), {
        'DESCRIPTOR': _SEARCHSUGGESTENTRY_PACKAGENAMECONTAINER,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:SearchSuggestEntry.PackageNameContainer)
    })
    ,
    'DESCRIPTOR': _SEARCHSUGGESTENTRY,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:SearchSuggestEntry)
})
_sym_db.RegisterMessage(SearchSuggestEntry)
_sym_db.RegisterMessage(SearchSuggestEntry.ImageContainer)
_sym_db.RegisterMessage(SearchSuggestEntry.PackageNameContainer)

TestingProgramResponse = _reflection.GeneratedProtocolMessageType('TestingProgramResponse', (_message.Message,), {
    'DESCRIPTOR': _TESTINGPROGRAMRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TestingProgramResponse)
})
_sym_db.RegisterMessage(TestingProgramResponse)

TestingProgramResult = _reflection.GeneratedProtocolMessageType('TestingProgramResult', (_message.Message,), {
    'DESCRIPTOR': _TESTINGPROGRAMRESULT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TestingProgramResult)
})
_sym_db.RegisterMessage(TestingProgramResult)

TestingProgramDetails = _reflection.GeneratedProtocolMessageType('TestingProgramDetails', (_message.Message,), {
    'DESCRIPTOR': _TESTINGPROGRAMDETAILS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TestingProgramDetails)
})
_sym_db.RegisterMessage(TestingProgramDetails)

LogRequest = _reflection.GeneratedProtocolMessageType('LogRequest', (_message.Message,), {
    'DESCRIPTOR': _LOGREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:LogRequest)
})
_sym_db.RegisterMessage(LogRequest)

TestingProgramRequest = _reflection.GeneratedProtocolMessageType('TestingProgramRequest', (_message.Message,), {
    'DESCRIPTOR': _TESTINGPROGRAMREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:TestingProgramRequest)
})
_sym_db.RegisterMessage(TestingProgramRequest)

UploadDeviceConfigRequest = _reflection.GeneratedProtocolMessageType('UploadDeviceConfigRequest', (_message.Message,), {
    'DESCRIPTOR': _UPLOADDEVICECONFIGREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UploadDeviceConfigRequest)
})
_sym_db.RegisterMessage(UploadDeviceConfigRequest)

UploadDeviceConfigResponse = _reflection.GeneratedProtocolMessageType('UploadDeviceConfigResponse', (_message.Message,),
                                                                      {
                                                                          'DESCRIPTOR': _UPLOADDEVICECONFIGRESPONSE,
                                                                          '__module__': 'googleplay_pb2'
                                                                          # @@protoc_insertion_point(class_scope:UploadDeviceConfigResponse)
                                                                      })
_sym_db.RegisterMessage(UploadDeviceConfigResponse)

AndroidCheckinRequest = _reflection.GeneratedProtocolMessageType('AndroidCheckinRequest', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDCHECKINREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidCheckinRequest)
})
_sym_db.RegisterMessage(AndroidCheckinRequest)

AndroidCheckinResponse = _reflection.GeneratedProtocolMessageType('AndroidCheckinResponse', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDCHECKINRESPONSE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidCheckinResponse)
})
_sym_db.RegisterMessage(AndroidCheckinResponse)

GservicesSetting = _reflection.GeneratedProtocolMessageType('GservicesSetting', (_message.Message,), {
    'DESCRIPTOR': _GSERVICESSETTING,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:GservicesSetting)
})
_sym_db.RegisterMessage(GservicesSetting)

AndroidBuildProto = _reflection.GeneratedProtocolMessageType('AndroidBuildProto', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDBUILDPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidBuildProto)
})
_sym_db.RegisterMessage(AndroidBuildProto)

AndroidCheckinProto = _reflection.GeneratedProtocolMessageType('AndroidCheckinProto', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDCHECKINPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidCheckinProto)
})
_sym_db.RegisterMessage(AndroidCheckinProto)

AndroidEventProto = _reflection.GeneratedProtocolMessageType('AndroidEventProto', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDEVENTPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidEventProto)
})
_sym_db.RegisterMessage(AndroidEventProto)

AndroidIntentProto = _reflection.GeneratedProtocolMessageType('AndroidIntentProto', (_message.Message,), {

    'Extra': _reflection.GeneratedProtocolMessageType('Extra', (_message.Message,), {
        'DESCRIPTOR': _ANDROIDINTENTPROTO_EXTRA,
        '__module__': 'googleplay_pb2'
        # @@protoc_insertion_point(class_scope:AndroidIntentProto.Extra)
    })
    ,
    'DESCRIPTOR': _ANDROIDINTENTPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidIntentProto)
})
_sym_db.RegisterMessage(AndroidIntentProto)
_sym_db.RegisterMessage(AndroidIntentProto.Extra)

AndroidStatisticProto = _reflection.GeneratedProtocolMessageType('AndroidStatisticProto', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDSTATISTICPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidStatisticProto)
})
_sym_db.RegisterMessage(AndroidStatisticProto)

ClientLibraryState = _reflection.GeneratedProtocolMessageType('ClientLibraryState', (_message.Message,), {
    'DESCRIPTOR': _CLIENTLIBRARYSTATE,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ClientLibraryState)
})
_sym_db.RegisterMessage(ClientLibraryState)

AndroidDataUsageProto = _reflection.GeneratedProtocolMessageType('AndroidDataUsageProto', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDDATAUSAGEPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidDataUsageProto)
})
_sym_db.RegisterMessage(AndroidDataUsageProto)

AndroidUsageStatsReport = _reflection.GeneratedProtocolMessageType('AndroidUsageStatsReport', (_message.Message,), {
    'DESCRIPTOR': _ANDROIDUSAGESTATSREPORT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AndroidUsageStatsReport)
})
_sym_db.RegisterMessage(AndroidUsageStatsReport)

AppBucket = _reflection.GeneratedProtocolMessageType('AppBucket', (_message.Message,), {
    'DESCRIPTOR': _APPBUCKET,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:AppBucket)
})
_sym_db.RegisterMessage(AppBucket)

CounterData = _reflection.GeneratedProtocolMessageType('CounterData', (_message.Message,), {
    'DESCRIPTOR': _COUNTERDATA,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:CounterData)
})
_sym_db.RegisterMessage(CounterData)

IpLayerAppStat = _reflection.GeneratedProtocolMessageType('IpLayerAppStat', (_message.Message,), {
    'DESCRIPTOR': _IPLAYERAPPSTAT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:IpLayerAppStat)
})
_sym_db.RegisterMessage(IpLayerAppStat)

IpLayerNetworkBucket = _reflection.GeneratedProtocolMessageType('IpLayerNetworkBucket', (_message.Message,), {
    'DESCRIPTOR': _IPLAYERNETWORKBUCKET,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:IpLayerNetworkBucket)
})
_sym_db.RegisterMessage(IpLayerNetworkBucket)

IpLayerNetworkStat = _reflection.GeneratedProtocolMessageType('IpLayerNetworkStat', (_message.Message,), {
    'DESCRIPTOR': _IPLAYERNETWORKSTAT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:IpLayerNetworkStat)
})
_sym_db.RegisterMessage(IpLayerNetworkStat)

KeyToPackageNameMapping = _reflection.GeneratedProtocolMessageType('KeyToPackageNameMapping', (_message.Message,), {
    'DESCRIPTOR': _KEYTOPACKAGENAMEMAPPING,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:KeyToPackageNameMapping)
})
_sym_db.RegisterMessage(KeyToPackageNameMapping)

PackageInfo = _reflection.GeneratedProtocolMessageType('PackageInfo', (_message.Message,), {
    'DESCRIPTOR': _PACKAGEINFO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PackageInfo)
})
_sym_db.RegisterMessage(PackageInfo)

PayloadLevelAppStat = _reflection.GeneratedProtocolMessageType('PayloadLevelAppStat', (_message.Message,), {
    'DESCRIPTOR': _PAYLOADLEVELAPPSTAT,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:PayloadLevelAppStat)
})
_sym_db.RegisterMessage(PayloadLevelAppStat)

StatCounters = _reflection.GeneratedProtocolMessageType('StatCounters', (_message.Message,), {
    'DESCRIPTOR': _STATCOUNTERS,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:StatCounters)
})
_sym_db.RegisterMessage(StatCounters)

UsageStatsExtensionProto = _reflection.GeneratedProtocolMessageType('UsageStatsExtensionProto', (_message.Message,), {
    'DESCRIPTOR': _USAGESTATSEXTENSIONPROTO,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UsageStatsExtensionProto)
})
_sym_db.RegisterMessage(UsageStatsExtensionProto)

ModifyLibraryRequest = _reflection.GeneratedProtocolMessageType('ModifyLibraryRequest', (_message.Message,), {
    'DESCRIPTOR': _MODIFYLIBRARYREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:ModifyLibraryRequest)
})
_sym_db.RegisterMessage(ModifyLibraryRequest)

UrlRequestWrapper = _reflection.GeneratedProtocolMessageType('UrlRequestWrapper', (_message.Message,), {
    'DESCRIPTOR': _URLREQUESTWRAPPER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:UrlRequestWrapper)
})
_sym_db.RegisterMessage(UrlRequestWrapper)

DeveloperAppsRequest = _reflection.GeneratedProtocolMessageType('DeveloperAppsRequest', (_message.Message,), {
    'DESCRIPTOR': _DEVELOPERAPPSREQUEST,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DeveloperAppsRequest)
})
_sym_db.RegisterMessage(DeveloperAppsRequest)

DeveloperIdContainer = _reflection.GeneratedProtocolMessageType('DeveloperIdContainer', (_message.Message,), {
    'DESCRIPTOR': _DEVELOPERIDCONTAINER,
    '__module__': 'googleplay_pb2'
    # @@protoc_insertion_point(class_scope:DeveloperIdContainer)
})
_sym_db.RegisterMessage(DeveloperIdContainer)

if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _ANDROIDAPPDELIVERYDATA._serialized_start = 21
    _ANDROIDAPPDELIVERYDATA._serialized_end = 507
    _SPLIT._serialized_start = 510
    _SPLIT._serialized_end = 645
    _ANDROIDAPPPATCHDATA._serialized_start = 648
    _ANDROIDAPPPATCHDATA._serialized_end = 776
    _APPFILEMETADATA._serialized_start = 779
    _APPFILEMETADATA._serialized_end = 933
    _ENCRYPTIONPARAMS._serialized_start = 935
    _ENCRYPTIONPARAMS._serialized_end = 1010
    _HTTPCOOKIE._serialized_start = 1012
    _HTTPCOOKIE._serialized_end = 1053
    _ADDRESS._serialized_start = 1056
    _ADDRESS._serialized_end = 1357
    _BOOKAUTHOR._serialized_start = 1359
    _BOOKAUTHOR._serialized_end = 1433
    _BOOKDETAILS._serialized_start = 1436
    _BOOKDETAILS._serialized_end = 1887
    _BOOKDETAILS_IDENTIFIER._serialized_start = 1841
    _BOOKDETAILS_IDENTIFIER._serialized_end = 1887
    _BOOKSUBJECT._serialized_start = 1889
    _BOOKSUBJECT._serialized_end = 1950
    _BROWSELINK._serialized_start = 1952
    _BROWSELINK._serialized_end = 2078
    _UNKNOWNCATEGORYCONTAINER._serialized_start = 2080
    _UNKNOWNCATEGORYCONTAINER._serialized_end = 2157
    _CATEGORYIDCONTAINER._serialized_start = 2159
    _CATEGORYIDCONTAINER._serialized_end = 2200
    _BROWSERESPONSE._serialized_start = 2203
    _BROWSERESPONSE._serialized_end = 2369
    _CATEGORYCONTAINER._serialized_start = 2371
    _CATEGORYCONTAINER._serialized_end = 2421
    _ADDRESSCHALLENGE._serialized_start = 2424
    _ADDRESSCHALLENGE._serialized_end = 2695
    _AUTHENTICATIONCHALLENGE._serialized_start = 2698
    _AUTHENTICATIONCHALLENGE._serialized_end = 2937
    _BUYRESPONSE._serialized_start = 2940
    _BUYRESPONSE._serialized_end = 4116
    _BUYRESPONSE_CHECKOUTINFO._serialized_start = 3384
    _BUYRESPONSE_CHECKOUTINFO._serialized_end = 4116
    _BUYRESPONSE_CHECKOUTINFO_CHECKOUTOPTION._serialized_start = 3694
    _BUYRESPONSE_CHECKOUTINFO_CHECKOUTOPTION._serialized_end = 4116
    _CHALLENGE._serialized_start = 4118
    _CHALLENGE._serialized_end = 4233
    _FORMCHECKBOX._serialized_start = 4235
    _FORMCHECKBOX._serialized_end = 4305
    _LINEITEM._serialized_start = 4307
    _LINEITEM._serialized_end = 4399
    _MONEY._serialized_start = 4401
    _MONEY._serialized_end = 4471
    _PURCHASENOTIFICATIONRESPONSE._serialized_start = 4474
    _PURCHASENOTIFICATIONRESPONSE._serialized_end = 4602
    _PURCHASESTATUSRESPONSE._serialized_start = 4605
    _PURCHASESTATUSRESPONSE._serialized_end = 4854
    _DELIVERYRESPONSE._serialized_start = 4856
    _DELIVERYRESPONSE._serialized_end = 4924
    _DOCID._serialized_start = 4926
    _DOCID._serialized_end = 4986
    _INSTALL._serialized_start = 4988
    _INSTALL._serialized_end = 5050
    _OFFER._serialized_start = 5053
    _OFFER._serialized_end = 5515
    _OWNERSHIPINFO._serialized_start = 5518
    _OWNERSHIPINFO._serialized_end = 5695
    _RENTALTERMS._serialized_start = 5697
    _RENTALTERMS._serialized_end = 5769
    _SUBSCRIPTIONTERMS._serialized_start = 5771
    _SUBSCRIPTIONTERMS._serialized_end = 5862
    _TIMEPERIOD._serialized_start = 5864
    _TIMEPERIOD._serialized_end = 5905
    _BILLINGADDRESSSPEC._serialized_start = 5907
    _BILLINGADDRESSSPEC._serialized_end = 5978
    _CARRIERBILLINGCREDENTIALS._serialized_start = 5980
    _CARRIERBILLINGCREDENTIALS._serialized_end = 6042
    _CARRIERBILLINGINSTRUMENT._serialized_start = 6045
    _CARRIERBILLINGINSTRUMENT._serialized_end = 6342
    _CARRIERBILLINGINSTRUMENTSTATUS._serialized_start = 6345
    _CARRIERBILLINGINSTRUMENTSTATUS._serialized_end = 6547
    _CARRIERTOS._serialized_start = 6550
    _CARRIERTOS._serialized_end = 6692
    _CARRIERTOSENTRY._serialized_start = 6694
    _CARRIERTOSENTRY._serialized_end = 6741
    _CREDITCARDINSTRUMENT._serialized_start = 6744
    _CREDITCARDINSTRUMENT._serialized_end = 6906
    _EFEPARAM._serialized_start = 6908
    _EFEPARAM._serialized_end = 6946
    _INPUTVALIDATIONERROR._serialized_start = 6948
    _INPUTVALIDATIONERROR._serialized_end = 7012
    _INSTRUMENT._serialized_start = 7015
    _INSTRUMENT._serialized_end = 7337
    _PASSWORDPROMPT._serialized_start = 7339
    _PASSWORDPROMPT._serialized_end = 7398
    _CONTAINERMETADATA._serialized_start = 7401
    _CONTAINERMETADATA._serialized_end = 7547
    _DEBUGINFO._serialized_start = 7549
    _DEBUGINFO._serialized_end = 7654
    _DEBUGINFO_TIMING._serialized_start = 7614
    _DEBUGINFO_TIMING._serialized_end = 7654
    _BULKDETAILSENTRY._serialized_start = 7656
    _BULKDETAILSENTRY._serialized_end = 7695
    _BULKDETAILSREQUEST._serialized_start = 7697
    _BULKDETAILSREQUEST._serialized_end = 7758
    _BULKDETAILSRESPONSE._serialized_start = 7760
    _BULKDETAILSRESPONSE._serialized_end = 7815
    _DETAILSRESPONSE._serialized_start = 7818
    _DETAILSRESPONSE._serialized_end = 8093
    _BADGE._serialized_start = 8095
    _BADGE._serialized_end = 8200
    _BADGECONTAINER1._serialized_start = 8202
    _BADGECONTAINER1._serialized_end = 8262
    _BADGECONTAINER2._serialized_start = 8264
    _BADGECONTAINER2._serialized_end = 8330
    _BADGELINKCONTAINER._serialized_start = 8332
    _BADGELINKCONTAINER._serialized_end = 8366
    _FEATURES._serialized_start = 8368
    _FEATURES._serialized_end = 8446
    _FEATURE._serialized_start = 8448
    _FEATURE._serialized_end = 8487
    _DEVICECONFIGURATIONPROTO._serialized_start = 8490
    _DEVICECONFIGURATIONPROTO._serialized_end = 8927
    _DOCUMENT._serialized_start = 8930
    _DOCUMENT._serialized_end = 9441
    _DOCUMENTVARIANT._serialized_start = 9444
    _DOCUMENTVARIANT._serialized_end = 9701
    _IMAGE._serialized_start = 9704
    _IMAGE._serialized_end = 10062
    _IMAGE_DIMENSION._serialized_start = 9971
    _IMAGE_DIMENSION._serialized_end = 10013
    _IMAGE_CITATION._serialized_start = 10015
    _IMAGE_CITATION._serialized_end = 10062
    _TRANSLATEDTEXT._serialized_start = 10064
    _TRANSLATEDTEXT._serialized_end = 10138
    _PLUSONEDATA._serialized_start = 10140
    _PLUSONEDATA._serialized_end = 10245
    _PLUSPERSON._serialized_start = 10247
    _PLUSPERSON._serialized_end = 10305
    _ALBUMDETAILS._serialized_start = 10307
    _ALBUMDETAILS._serialized_end = 10406
    _APPDETAILS._serialized_start = 10409
    _APPDETAILS._serialized_end = 11046
    _DEPENDENCIES._serialized_start = 11048
    _DEPENDENCIES._serialized_end = 11149
    _DEPENDENCY._serialized_start = 11151
    _DEPENDENCY._serialized_end = 11219
    _TESTINGPROGRAMINFO._serialized_start = 11221
    _TESTINGPROGRAMINFO._serialized_end = 11311
    _EARLYACCESSINFO._serialized_start = 11313
    _EARLYACCESSINFO._serialized_end = 11345
    _ARTISTDETAILS._serialized_start = 11347
    _ARTISTDETAILS._serialized_end = 11441
    _ARTISTEXTERNALLINKS._serialized_start = 11443
    _ARTISTEXTERNALLINKS._serialized_end = 11541
    _DOCUMENTDETAILS._serialized_start = 11544
    _DOCUMENTDETAILS._serialized_end = 11998
    _FILEMETADATA._serialized_start = 12000
    _FILEMETADATA._serialized_end = 12067
    _MAGAZINEDETAILS._serialized_start = 12070
    _MAGAZINEDETAILS._serialized_end = 12218
    _MUSICDETAILS._serialized_start = 12221
    _MUSICDETAILS._serialized_end = 12408
    _SONGDETAILS._serialized_start = 12411
    _SONGDETAILS._serialized_end = 12569
    _SUBSCRIPTIONDETAILS._serialized_start = 12571
    _SUBSCRIPTIONDETAILS._serialized_end = 12620
    _TRAILER._serialized_start = 12622
    _TRAILER._serialized_end = 12723
    _TVEPISODEDETAILS._serialized_start = 12725
    _TVEPISODEDETAILS._serialized_end = 12812
    _TVSEASONDETAILS._serialized_start = 12814
    _TVSEASONDETAILS._serialized_end = 12920
    _TVSHOWDETAILS._serialized_start = 12922
    _TVSHOWDETAILS._serialized_end = 13015
    _VIDEOCREDIT._serialized_start = 13017
    _VIDEOCREDIT._serialized_end = 13080
    _VIDEODETAILS._serialized_start = 13083
    _VIDEODETAILS._serialized_end = 13302
    _VIDEORENTALTERM._serialized_start = 13305
    _VIDEORENTALTERM._serialized_end = 13465
    _VIDEORENTALTERM_TERM._serialized_start = 13429
    _VIDEORENTALTERM_TERM._serialized_end = 13465
    _BUCKET._serialized_start = 13468
    _BUCKET._serialized_end = 13717
    _LISTRESPONSE._serialized_start = 13719
    _LISTRESPONSE._serialized_end = 13779
    _DOCV1._serialized_start = 13782
    _DOCV1._serialized_end = 14186
    _DOCV2._serialized_start = 14189
    _DOCV2._serialized_end = 14916
    _UNKNOWN25._serialized_start = 14918
    _UNKNOWN25._serialized_end = 14959
    _UNKNOWN25ITEM._serialized_start = 14961
    _UNKNOWN25ITEM._serialized_end = 15031
    _UNKNOWN25CONTAINER._serialized_start = 15033
    _UNKNOWN25CONTAINER._serialized_end = 15068
    _RELATEDLINKS._serialized_start = 15071
    _RELATEDLINKS._serialized_end = 15288
    _RELATEDLINKSUNKNOWN1._serialized_start = 15290
    _RELATEDLINKSUNKNOWN1._serialized_end = 15353
    _RELATEDLINKSUNKNOWN2._serialized_start = 15355
    _RELATEDLINKSUNKNOWN2._serialized_end = 15415
    _RATED._serialized_start = 15417
    _RATED._serialized_end = 15489
    _RELATEDLINK._serialized_start = 15491
    _RELATEDLINK._serialized_end = 15547
    _CATEGORYINFO._serialized_start = 15549
    _CATEGORYINFO._serialized_end = 15601
    _ENCRYPTEDSUBSCRIBERINFO._serialized_start = 15604
    _ENCRYPTEDSUBSCRIBERINFO._serialized_end = 15757
    _AVAILABILITY._serialized_start = 15760
    _AVAILABILITY._serialized_end = 16205
    _AVAILABILITY_PERDEVICEAVAILABILITYRESTRICTION._serialized_start = 16063
    _AVAILABILITY_PERDEVICEAVAILABILITYRESTRICTION._serialized_end = 16205
    _FILTEREVALUATIONINFO._serialized_start = 16207
    _FILTEREVALUATIONINFO._serialized_end = 16270
    _RULE._serialized_start = 16273
    _RULE._serialized_end = 16485
    _RULEEVALUATION._serialized_start = 16488
    _RULEEVALUATION._serialized_end = 16629
    _LIBRARYAPPDETAILS._serialized_start = 16631
    _LIBRARYAPPDETAILS._serialized_end = 16749
    _LIBRARYINAPPDETAILS._serialized_start = 16751
    _LIBRARYINAPPDETAILS._serialized_end = 16819
    _LIBRARYMUTATION._serialized_start = 16822
    _LIBRARYMUTATION._serialized_end = 17062
    _LIBRARYSUBSCRIPTIONDETAILS._serialized_start = 17065
    _LIBRARYSUBSCRIPTIONDETAILS._serialized_end = 17214
    _LIBRARYUPDATE._serialized_start = 17217
    _LIBRARYUPDATE._serialized_end = 17357
    _ANDROIDAPPNOTIFICATIONDATA._serialized_start = 17359
    _ANDROIDAPPNOTIFICATIONDATA._serialized_end = 17425
    _INAPPNOTIFICATIONDATA._serialized_start = 17427
    _INAPPNOTIFICATIONDATA._serialized_end = 17504
    _LIBRARYDIRTYDATA._serialized_start = 17506
    _LIBRARYDIRTYDATA._serialized_end = 17541
    _NOTIFICATION._serialized_start = 17544
    _NOTIFICATION._serialized_end = 18079
    _PURCHASEDECLINEDDATA._serialized_start = 18081
    _PURCHASEDECLINEDDATA._serialized_end = 18145
    _PURCHASEREMOVALDATA._serialized_start = 18147
    _PURCHASEREMOVALDATA._serialized_end = 18187
    _USERNOTIFICATIONDATA._serialized_start = 18190
    _USERNOTIFICATIONDATA._serialized_end = 18326
    _AGGREGATERATING._serialized_start = 18329
    _AGGREGATERATING._serialized_end = 18624
    _ACCEPTTOSRESPONSE._serialized_start = 18626
    _ACCEPTTOSRESPONSE._serialized_end = 18645
    _CARRIERBILLINGCONFIG._serialized_start = 18648
    _CARRIERBILLINGCONFIG._serialized_end = 18881
    _BILLINGCONFIG._serialized_start = 18883
    _BILLINGCONFIG._serialized_end = 18977
    _CORPUSMETADATA._serialized_start = 18980
    _CORPUSMETADATA._serialized_end = 19109
    _EXPERIMENTS._serialized_start = 19111
    _EXPERIMENTS._serialized_end = 19146
    _SELFUPDATECONFIG._serialized_start = 19148
    _SELFUPDATECONFIG._serialized_end = 19199
    _TOCRESPONSE._serialized_start = 19202
    _TOCRESPONSE._serialized_end = 19763
    _PAYLOAD._serialized_start = 19766
    _PAYLOAD._serialized_end = 20532
    _PREFETCH._serialized_start = 20534
    _PREFETCH._serialized_end = 20637
    _SERVERMETADATA._serialized_start = 20639
    _SERVERMETADATA._serialized_end = 20678
    _TARGETS._serialized_start = 20680
    _TARGETS._serialized_end = 20726
    _SERVERCOOKIE._serialized_start = 20728
    _SERVERCOOKIE._serialized_end = 20771
    _SERVERCOOKIES._serialized_start = 20773
    _SERVERCOOKIES._serialized_end = 20825
    _RESPONSEWRAPPER._serialized_start = 20828
    _RESPONSEWRAPPER._serialized_end = 21106
    _RESPONSEWRAPPERAPI._serialized_start = 21108
    _RESPONSEWRAPPERAPI._serialized_end = 21158
    _PAYLOADAPI._serialized_start = 21160
    _PAYLOADAPI._serialized_end = 21223
    _USERPROFILERESPONSE._serialized_start = 21225
    _USERPROFILERESPONSE._serialized_end = 21281
    _SERVERCOMMANDS._serialized_start = 21283
    _SERVERCOMMANDS._serialized_end = 21376
    _GETREVIEWSRESPONSE._serialized_start = 21378
    _GETREVIEWSRESPONSE._serialized_end = 21446
    _REVIEW._serialized_start = 21449
    _REVIEW._serialized_end = 21758
    _REVIEWAUTHOR._serialized_start = 21760
    _REVIEWAUTHOR._serialized_end = 21812
    _USERPROFILE._serialized_start = 21815
    _USERPROFILE._serialized_end = 21993
    _REVIEWRESPONSE._serialized_start = 21995
    _REVIEWRESPONSE._serialized_end = 22103
    _RELATEDSEARCH._serialized_start = 22105
    _RELATEDSEARCH._serialized_end = 22208
    _SEARCHRESPONSE._serialized_start = 22211
    _SEARCHRESPONSE._serialized_end = 22404
    _SEARCHSUGGESTRESPONSE._serialized_start = 22406
    _SEARCHSUGGESTRESPONSE._serialized_end = 22465
    _SEARCHSUGGESTENTRY._serialized_start = 22468
    _SEARCHSUGGESTENTRY._serialized_end = 22754
    _SEARCHSUGGESTENTRY_IMAGECONTAINER._serialized_start = 22675
    _SEARCHSUGGESTENTRY_IMAGECONTAINER._serialized_end = 22709
    _SEARCHSUGGESTENTRY_PACKAGENAMECONTAINER._serialized_start = 22711
    _SEARCHSUGGESTENTRY_PACKAGENAMECONTAINER._serialized_end = 22754
    _TESTINGPROGRAMRESPONSE._serialized_start = 22756
    _TESTINGPROGRAMRESPONSE._serialized_end = 22819
    _TESTINGPROGRAMRESULT._serialized_start = 22821
    _TESTINGPROGRAMRESULT._serialized_end = 22884
    _TESTINGPROGRAMDETAILS._serialized_start = 22886
    _TESTINGPROGRAMDETAILS._serialized_end = 22958
    _LOGREQUEST._serialized_start = 22960
    _LOGREQUEST._serialized_end = 23026
    _TESTINGPROGRAMREQUEST._serialized_start = 23028
    _TESTINGPROGRAMREQUEST._serialized_end = 23091
    _UPLOADDEVICECONFIGREQUEST._serialized_start = 23094
    _UPLOADDEVICECONFIGREQUEST._serialized_end = 23226
    _UPLOADDEVICECONFIGRESPONSE._serialized_start = 23228
    _UPLOADDEVICECONFIGRESPONSE._serialized_end = 23289
    _ANDROIDCHECKINREQUEST._serialized_start = 23292
    _ANDROIDCHECKINREQUEST._serialized_end = 23779
    _ANDROIDCHECKINRESPONSE._serialized_start = 23782
    _ANDROIDCHECKINRESPONSE._serialized_end = 24074
    _GSERVICESSETTING._serialized_start = 24076
    _GSERVICESSETTING._serialized_end = 24123
    _ANDROIDBUILDPROTO._serialized_start = 24126
    _ANDROIDBUILDPROTO._serialized_end = 24402
    _ANDROIDCHECKINPROTO._serialized_start = 24405
    _ANDROIDCHECKINPROTO._serialized_end = 24663
    _ANDROIDEVENTPROTO._serialized_start = 24665
    _ANDROIDEVENTPROTO._serialized_end = 24730
    _ANDROIDINTENTPROTO._serialized_start = 24733
    _ANDROIDINTENTPROTO._serialized_end = 24903
    _ANDROIDINTENTPROTO_EXTRA._serialized_start = 24867
    _ANDROIDINTENTPROTO_EXTRA._serialized_end = 24903
    _ANDROIDSTATISTICPROTO._serialized_start = 24905
    _ANDROIDSTATISTICPROTO._serialized_end = 24969
    _CLIENTLIBRARYSTATE._serialized_start = 24971
    _CLIENTLIBRARYSTATE._serialized_end = 25089
    _ANDROIDDATAUSAGEPROTO._serialized_start = 25092
    _ANDROIDDATAUSAGEPROTO._serialized_end = 25318
    _ANDROIDUSAGESTATSREPORT._serialized_start = 25320
    _ANDROIDUSAGESTATSREPORT._serialized_end = 25430
    _APPBUCKET._serialized_start = 25432
    _APPBUCKET._serialized_end = 25557
    _COUNTERDATA._serialized_start = 25559
    _COUNTERDATA._serialized_end = 25604
    _IPLAYERAPPSTAT._serialized_start = 25606
    _IPLAYERAPPSTAT._serialized_end = 25704
    _IPLAYERNETWORKBUCKET._serialized_start = 25707
    _IPLAYERNETWORKBUCKET._serialized_end = 25850
    _IPLAYERNETWORKSTAT._serialized_start = 25853
    _IPLAYERNETWORKSTAT._serialized_end = 26005
    _KEYTOPACKAGENAMEMAPPING._serialized_start = 26007
    _KEYTOPACKAGENAMEMAPPING._serialized_end = 26110
    _PACKAGEINFO._serialized_start = 26112
    _PACKAGEINFO._serialized_end = 26163
    _PAYLOADLEVELAPPSTAT._serialized_start = 26165
    _PAYLOADLEVELAPPSTAT._serialized_end = 26273
    _STATCOUNTERS._serialized_start = 26275
    _STATCOUNTERS._serialized_end = 26379
    _USAGESTATSEXTENSIONPROTO._serialized_start = 26381
    _USAGESTATSEXTENSIONPROTO._serialized_end = 26450
    _MODIFYLIBRARYREQUEST._serialized_start = 26452
    _MODIFYLIBRARYREQUEST._serialized_end = 26544
    _URLREQUESTWRAPPER._serialized_start = 26546
    _URLREQUESTWRAPPER._serialized_end = 26618
    _DEVELOPERAPPSREQUEST._serialized_start = 26621
    _DEVELOPERAPPSREQUEST._serialized_end = 26772
    _DEVELOPERIDCONTAINER._serialized_start = 26774
    _DEVELOPERIDCONTAINER._serialized_end = 26859
# @@protoc_insertion_point(module_scope)
