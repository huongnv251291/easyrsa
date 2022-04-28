from multiprocessing import Pool


def search_worker(article_and_keyword):
    # unpack the tuple
    article, keyword = article_and_keyword

    # count occurrences
    score = 0
    if keyword in article:
        score += 1

    return score


if __name__ == "__main__":
    # the article and the keywords
    article = """The multiprocessing package also includes some APIs that are not in the threading module at all. For 
    example, there is a neat Pool class that you can use to parallelize executing a function across multiple inputs. """
    keywords = ["threading", "package", "parallelize","Pool"]

    # construct the arguments for the search_worker; one keyword per worker but same article
    args = [(article, keyword) for keyword in keywords]

    # construct the pool and map to the workers
    with Pool(3) as pool:
        result = pool.map(search_worker, args)
    print(result)
