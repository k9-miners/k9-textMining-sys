function extractHostname(url) {
    var hostname;
    //find & remove protocol (http, ftp, etc.) and get hostname

    if (url.indexOf("//") > -1) {
        hostname = url.split('/')[2];
    }
    else {
        hostname = url.split('/')[0];
    }

    //find & remove port number
    hostname = hostname.split(':')[0];
    //find & remove "?"
    hostname = hostname.split('?')[0];

    return hostname;
}

// Function to process the posts
function raw_data(post)
{
    // Process each post into a result blog
    post.forEach(post => {
        var doc_id = post['doc_id'];
        var doc_url = post['doc_url'];

        if (window.matchMedia('(max-width: 700px)').matches)
        {
            var hostName = extractHostname(doc_url);
            var directory = doc_url.split('/')[3];
            var modifiedUrl = 'https://' + hostName + ' > ' + directory;
        } 
        else
        {
            var modifiedUrl = doc_url;
        }
        // var length = 50; 
        // var trimmedString = doc_url.length > length ? doc_url.substring(0, length - 3) + "..." : doc_url.substring(0, length);
        var doc_title = post['doc_title'];
        var doc_content = post['doc_content'];
        var concordance = post['concordance'];
        var token = post['query_term'];
        
        
        var result_blog_title = document.createElement("div");
        var result_blog_link = document.createElement("a");
        result_blog_title.id = 'result_blog_title';
        result_blog_link.id = 'result_blog_link-'+doc_id;
        result_blog_link.href = doc_url;
        result_blog_link.append(doc_title);
        result_blog_title.append(result_blog_link);

        var result_blog_url = document.createElement("div");
        result_blog_url.id = 'result_blog_url';
        result_blog_url.append(modifiedUrl);

        var separateLine = document.createElement("div");
        separateLine.id = 'separateLine';

        var result_concordance = document.createElement("div");
        result_concordance.id = 'result_concordance';
        result_concordance.append(separateLine);
        result_concordance.append(concordance);

        var result_blog = document.createElement("div");
        result_blog.className = 'result_blog' 

        var blog_id = document.createElement("div");
        blog_id.id = doc_id;
        blog_id.style.padding = "5px 30px 0px 30px"
        blog_id.append(result_blog_title);
        blog_id.append(result_blog_url);
        blog_id.append(result_concordance);
        result_blog.append(blog_id)

        var result_blog_container = document.getElementById('result_blog_container');
        result_blog_container.append(result_blog);
    });

    // ------------------------------------------------------------------
    // Section to call the pagination when the pagination list is triggered
    // ------------------------------------------------------------------
    // Amount of element to be displayed in a single pagination
    var pageSize = 10;
    // Total amount of elements to be displayed
    var pagesCount = document.getElementById("result_blog_container").childElementCount;
    var totalPages = Math.ceil(pagesCount / pageSize)


    if(pagesCount <= 10)
    {
        $("#loadMore").text("No more relevant result");
    }
    else
    {
        $("#loadMore").text("Load More");
    }

    $('.pagination').twbsPagination({
        totalPages: totalPages,
        // Limit of the pagination number
        visiblePages: 5,
        onPageClick: function (event, page) {
            var startIndex = (pageSize*(page-1))
            var endIndex = startIndex + pageSize
            $('.result_blog').hide().filter(function(){
                var idx = $(this).index();
                return idx>=startIndex && idx<endIndex;
            }).show()

            $('body,html').animate({
                scrollTop: 0
            }, 400);
        }
    });

    var contentLeft = pagesCount - 10;

    // ------------------------------------------------------------------
    // Section to call trigger the load more button
    // ------------------------------------------------------------------
    $(function () {
        $(".result_blog").slice(0, 10).show();
        $("#loadMore").on('click', function (e) {
            var $elem = $(this);
            // store the background-color
            var oldBG = $elem.css('background-color');
            // change the background color to what you want
            $elem.css('backgroundColor', '#CACAC9');
            // after 1 second, change it back
            setTimeout(function() {
                $elem.css('background-color', oldBG);
            }, 500);
            e.preventDefault();
            $(".result_blog:hidden").slice(0, 10).slideDown();
            if ($(".result_blog:hidden").length == 0) {
                $("#load").fadeOut('slow');
            }
            contentLeft = contentLeft - 10;
            if(contentLeft < 10)
            {
                $elem.text("No more relevant result");
            }
        });
    });
}


